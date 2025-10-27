import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, Optional
from repository.base import Base
from model import Room


class RoomRepository(Base):
    def get_all_rooms(self) -> List[Room]:
        """获取所有房间"""
        try:
            query = "SELECT * FROM room"
            results = self.execute_query(query)
            return [Room.from_dict(row) for row in results] if results else []
        except Exception as e:
            print(f"获取所有房间失败: {e}")
            return []

    def get_room_by_id(self, room_id: int) -> Optional[Room]:
        """根据ID获取房间"""
        try:
            query = "SELECT * FROM room WHERE roomID = %s"
            result = self.execute_query(query, (room_id,))
            return Room.from_dict(result[0]) if result else None
        except Exception as e:
            print(f"获取房间失败: {e}")
            return None

    def get_rooms_by_office(self, office_id: int) -> List[Room]:
        """根据科室获取房间"""
        try:
            query = "SELECT * FROM room WHERE officeID = %s ORDER BY roomID"
            results = self.execute_query(query, (office_id,))
            return [Room.from_dict(row) for row in results] if results else []
        except Exception as e:
            print(f"获取科室房间失败: {e}")
            return []

    def get_rooms_by_office_ids(self, office_ids: List[int]) -> List[Room]:
        """根据科室ID列表获取房间"""
        try:
            if not office_ids:
                return []

            placeholders = ', '.join(['%s'] * len(office_ids))
            query = f"SELECT * FROM room WHERE officeID IN ({placeholders}) ORDER BY officeID, roomID"
            results = self.execute_query(query, tuple(office_ids))
            return [Room.from_dict(row) for row in results] if results else []
        except Exception as e:
            print(f"批量获取科室房间失败: {e}")
            return []

    def create_room(self, room_id: int, office_id: int) -> bool:
        """创建房间"""
        try:
            query = "INSERT INTO room (roomID, officeID) VALUES (%s, %s)"
            result = self.execute_update(query, (room_id, office_id))
            return result > 0
        except Exception as e:
            print(f"创建房间失败: {e}")
            return False

    def delete_room(self, room_id: int) -> bool:
        """删除房间"""
        try:
            query = "DELETE FROM room WHERE roomID = %s"
            result = self.execute_update(query, (room_id,))
            return result > 0
        except Exception as e:
            print(f"删除房间失败: {e}")
            return False

    def get_office_room_count(self, office_id: int) -> int:
        """获取科室的房间数量"""
        try:
            query = "SELECT COUNT(*) as count FROM room WHERE officeID = %s"
            result = self.execute_query(query, (office_id,))
            return result[0]['count'] if result else 0
        except Exception as e:
            print(f"获取科室房间数量失败: {e}")
            return 0

    def get_available_rooms_by_office_and_time(self, office_id: int, date: str, timeslot_id: int) -> List[Room]:
        """获取科室在指定时间可用的房间（未被占用的房间）"""
        try:
            query = """
                    SELECT r.*
                    FROM room r
                    WHERE r.officeID = %s
                      AND r.roomID NOT IN (SELECT s.roomID \
                                           FROM section s \
                                           WHERE s.date = %s \
                                             AND s.timeslotID = %s)
                    ORDER BY r.roomID
                    """
            results = self.execute_query(query, (office_id, date, timeslot_id))
            return [Room.from_dict(row) for row in results] if results else []
        except Exception as e:
            print(f"获取可用房间失败: {e}")
            return []