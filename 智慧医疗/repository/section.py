import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mysql.connector
from mysql.connector import Error
from typing import List, Optional, Dict
from model import Section, DoctorDisplayView
from repository.base import Base


class SectionRepository(Base):
    # ==================== 基础查询函数 ====================

    # 根据ID获取排班信息
    def get_section_by_id(self, section_id: int) -> Optional[Section]:
        try:
            query = "SELECT * FROM section WHERE sectionID = %s"
            result = self.execute_query(query, (section_id,))
            return Section.from_dict(result[0]) if result else None
        except Exception as e:
            print(f"获取排班信息失败: {e}")
            return None

    # 根据日期获取所有排班
    def get_sections_by_date(self, date: str) -> List[Section]:
        """根据日期获取所有排班"""
        try:
            query = "SELECT * FROM section WHERE date = %s"
            results = self.execute_query(query, (date,))
            return [Section.from_dict(row) for row in results] if results else []
        except Exception as e:
            print(f"获取日期排班失败: {e}")
            return []

    # 获取医生某天的所有排班
    def get_sections_by_doctor_and_date(self, doctor_id: int, date: str) -> List[Section]:
        try:
            query = "SELECT * FROM section WHERE doctorID = %s AND date = %s"
            results = self.execute_query(query, (doctor_id, date))
            return [Section.from_dict(row) for row in results] if results else []
        except Exception as e:
            print(f"获取医生排班失败: {e}")
            return []

    # 获取科室某天的所有排班
    def get_sections_by_office_and_date(self, office_id: int, date: str) -> List[Section]:
        try:
            query = """
                    SELECT s.* 
                    FROM section s 
                             JOIN doctor d ON s.doctorID = d.doctorID
                    WHERE d.officeID = %s 
                      AND s.date = %s 
                    """
            results = self.execute_query(query, (office_id, date))
            return [Section.from_dict(row) for row in results] if results else []
        except Exception as e:
            print(f"获取科室排班失败: {e}")
            return []

    # ==================== 业务查询函数 ====================

    # 获取医生某天的排班信息
    def get_doctor_schedule_by_date(self, doctor_id: int, date: str) -> List[dict]:
        try:
            query = """
                    SELECT s.sectionID, t.starttime, t.endtime, s.restappiontment
                    FROM section s
                             JOIN timeslot t ON s.timeslotID = t.timeslotID
                    WHERE s.doctorID = %s 
                      AND s.date = %s 
                    """
            results = self.execute_query(query, (doctor_id, date))
            return results if results else []
        except Exception as e:
            print(f"获取医生排班信息失败: {e}")
            return []

    # 获取科室某天的排班信息
    def get_office_schedule_by_date(self, office_id: int, date: str) -> List[DoctorDisplayView]:
        """获取科室某天的排班信息 - 对应需求4（返回医生显示视图格式）"""
        # 先获取科室名称
        office_query = "SELECT name FROM office WHERE officeID = %s"
        office_result = self.execute_query(office_query, (office_id,))

        if not office_result:
            return []

        office_name = office_result[0]['name']

        query = """
                SELECT ddv.*, s.sectionID, t.starttime, t.endtime, s.restappiontment
                FROM section s
                         JOIN doctor_display_view ddv ON s.doctorID = ddv.doctorID
                         JOIN timeslot t ON s.timeslotID = t.timeslotID
                WHERE ddv.office_name = %s
                  AND s.date = %s
                """
        try:
            results = self.execute_query(query, (office_name, date))
            # 将结果转换为DoctorDisplayView对象列表
            doctor_views = []
            for row in results:
                # 提取医生显示视图的字段
                doctor_data = {
                    'doctorID': row.get('doctorID'),
                    'doctor_name': row.get('doctor_name'),
                    'age': row.get('age'),
                    'office_name': row.get('office_name'),
                    'expertise_name': row.get('expertise_name'),
                    'position_name': row.get('position_name'),
                    'NumberOfPatients': row.get('NumberOfPatients')
                }
                doctor_view = DoctorDisplayView.from_dict(doctor_data)

                # 添加排班信息到对象属性中
                doctor_view.sectionID = row.get('sectionID')
                doctor_view.starttime = row.get('starttime')
                doctor_view.endtime = row.get('endtime')
                doctor_view.restappiontment = row.get('restappiontment')

                doctor_views.append(doctor_view)

            return doctor_views
        except Exception as e:
            print(f"获取科室排班信息失败: {e}")
            return []

    # 获取当前时间段的挂号名额
    def get_current_timeslot_availability(self, office_id: int, date: str, timeslot_id: int) -> Dict:
        try:
            query = """
                    SELECT s.sectionID, s.restregistration, s.appiontmentconvert, s.roomID, d.name as doctor_name
                    FROM section s
                             JOIN doctor d ON s.doctorID = d.doctorID
                             JOIN room r ON s.roomID = r.roomID
                    WHERE r.officeID = %s
                      AND s.date = %s
                      AND s.timeslotID = %s
                    """
            results = self.execute_query(query, (office_id, date, timeslot_id))

            if results:
                # 计算实际可用挂号名额：剩余挂号名额 - 预约转挂号预留人数
                total_available_registration = sum(
                    max(0, result['restregistration'] - result['appiontmentconvert'])
                    for result in results
                )
                return {
                    "sectionID": results[0]['sectionID'],
                    "restregistration": total_available_registration,
                    "roomID": results[0]['roomID'],
                    "doctor_count": len(results)
                }
            else:
                return {
                    "sectionID": None,
                    "restregistration": 0,
                    "roomID": None,
                    "doctor_count": 0
                }
        except Exception as e:
            print(f"获取时间段可用性失败: {e}")
            return {"restregistration": 0}

    # ==================== 预约名额管理 ====================

    # 查询预约名额信息
    def get_appointment_quota(self, section_id: int) -> Dict[str, int]:
        try:
            query = "SELECT restappiontment, appiontmentconvert FROM section WHERE sectionID = %s"
            result = self.execute_query(query, (section_id,))
            if result:
                return {
                    "restappiontment": result[0]['restappiontment'],
                    "appiontmentconvert": result[0]['appiontmentconvert']
                }
            return {"restappiontment": 0, "appiontmentconvert": 0}
        except Exception as e:
            print(f"查询预约名额失败: {e}")
            return {"restappiontment": 0, "appiontmentconvert": 0}

    # 预约名额 -1 (患者预约时调用)
    def decrease_appointment_quota(self, section_id: int) -> bool:
        try:
            query = "UPDATE section SET restappiontment = restappiontment - 1 WHERE sectionID = %s AND restappiontment > 0"
            result = self.execute_update(query, (section_id,))
            return result > 0
        except Exception as e:
            print(f"减少预约名额失败: {e}")
            return False

    # 预约名额 +1 (取消预约时调用)
    def increase_appointment_quota(self, section_id: int) -> bool:
        try:
            query = "UPDATE section SET restappiontment = restappiontment + 1 WHERE sectionID = %s"
            result = self.execute_update(query, (section_id,))
            return result > 0
        except Exception as e:
            print(f"增加预约名额失败: {e}")
            return False

    # ==================== 挂号名额管理 ====================

    # 查询挂号名额信息
    def get_registration_quota(self, section_id: int) -> Dict[str, int]:
        try:
            query = "SELECT restregistration, totalregistration FROM section WHERE sectionID = %s"
            result = self.execute_query(query, (section_id,))
            if result:
                return {
                    "restregistration": result[0]['restregistration'],
                    "totalregistration": result[0]['totalregistration']
                }
            return {"restregistration": 0, "totalregistration": 0}
        except Exception as e:
            print(f"查询挂号名额失败: {e}")
            return {"restregistration": 0, "totalregistration": 0}

    # 挂号名额 -1 (患者挂号时调用)
    def decrease_registration_quota(self, section_id: int) -> bool:
        try:
            query = "UPDATE section SET restregistration = restregistration - 1 WHERE sectionID = %s AND restregistration > 0"
            result = self.execute_update(query, (section_id,))
            return result > 0
        except Exception as e:
            print(f"减少挂号名额失败: {e}")
            return False

    # 挂号名额 +1 (特殊情况下恢复名额)
    def increase_registration_quota(self, section_id: int) -> bool:
        try:
            query = "UPDATE section SET restregistration = restregistration + 1 WHERE sectionID = %s AND restregistration < totalregistration"
            result = self.execute_update(query, (section_id,))
            return result > 0
        except Exception as e:
            print(f"增加挂号名额失败: {e}")
            return False

    # ==================== 预约转挂号管理 ====================

    # 查询预约转挂号人数
    def get_appointment_convert_count(self, section_id: int) -> int:
        try:
            query = "SELECT appiontmentconvert FROM section WHERE sectionID = %s"
            result = self.execute_query(query, (section_id,))
            return result[0]['appiontmentconvert'] if result else 0
        except Exception as e:
            print(f"查询预约转挂号人数失败: {e}")
            return 0

    # 预约转挂号预留人数 +1 (患者预约时调用)
    def increase_appointment_convert(self, section_id: int) -> bool:
        try:
            query = "UPDATE section SET appiontmentconvert = appiontmentconvert + 1 WHERE sectionID = %s"
            result = self.execute_update(query, (section_id,))
            return result > 0
        except Exception as e:
            print(f"增加预约转挂号人数失败: {e}")
            return False

    # 预约转挂号预留人数 -1 (患者预约转挂号时调用)
    def decrease_appointment_convert(self, section_id: int) -> bool:
        try:
            query = "UPDATE section SET appiontmentconvert = appiontmentconvert - 1 WHERE sectionID = %s AND appiontmentconvert > 0"
            result = self.execute_update(query, (section_id,))
            return result > 0
        except Exception as e:
            print(f"减少预约转挂号人数失败: {e}")
            return False

    # ==================== 排班查询函数 ====================

    # 根据科室、日期、时间段获取排班
    def get_sections_by_office_and_timeslot(self, office_id: int, date: str, timeslot_id: int) -> List[Section]:
        try:
            query = """
            SELECT s.* FROM section s
            JOIN doctor d ON s.doctorID = d.doctorID
            WHERE d.officeID = %s AND s.date = %s AND s.timeslotID = %s
            """
            results = self.execute_query(query, (office_id, date, timeslot_id))
            return [Section.from_dict(row) for row in results] if results else []
        except Exception as e:
            print(f"获取科室时间段排班失败: {e}")
            return []

    # 检查排班是否还有挂号名额
    def check_registration_availability(self, section_id: int) -> bool:
        quota = self.get_registration_quota(section_id)
        return quota["restregistration"] > 0

    # 根据section获取该排班的所有挂号记录
    def get_registrations_by_section(self, section_id: int) -> List[Dict]:
        try:
            query = "SELECT * FROM registration WHERE sectionID = %s"
            return self.execute_query(query, (section_id,))
        except Exception as e:
            print(f"获取排班挂号记录失败: {e}")
            return []

    # 创建挂号记录
    def create_registration(self, patients_id: int, section_id: int, number: int) -> bool:
        try:
            query = "INSERT INTO registration (patientsID, sectionID, number, state) VALUES (%s, %s, %s, 'pending')"
            result = self.execute_update(query, (patients_id, section_id, number))
            return result > 0
        except Exception as e:
            print(f"创建挂号记录失败: {e}")
            return False

    # ==================== 创建排班 ====================
    def create_section(self, doctor_id: int, date: str, room_id: int, timeslot_id: int,
                       restappiontment: int = 10, appiontmentconvert: int = 0,
                       restregistration: int = 20, totalregistration: int = 20) -> bool:
        """创建排班记录"""
        try:
            query = """
                    INSERT INTO section
                    (doctorID, date, roomID, timeslotID, restappiontment,
                     appiontmentconvert, restregistration, totalregistration)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) \
                    """
            result = self.execute_update(query, (
                doctor_id, date, room_id, timeslot_id,
                restappiontment, appiontmentconvert,
                restregistration, totalregistration
            ))
            return result > 0
        except Exception as e:
            print(f"创建排班记录失败: {e}")
            return False

    def batch_create_sections(self, sections_data: List[Dict]) -> bool:
        """批量创建排班记录"""
        try:
            success_count = 0
            for section_data in sections_data:
                success = self.create_section(
                    doctor_id=section_data.get('doctorID'),
                    date=section_data.get('date'),
                    room_id=section_data.get('roomID'),
                    timeslot_id=section_data.get('timeslotID'),
                    restappiontment=section_data.get('restappiontment', 15),
                    appiontmentconvert=section_data.get('appiontmentconvert', 0),
                    restregistration=section_data.get('restregistration', 20),
                    totalregistration=section_data.get('totalregistration', 20)
                )
                if success:
                    success_count += 1

            print(f"批量创建排班记录: 成功 {success_count}/{len(sections_data)} 条")
            return success_count == len(sections_data)
        except Exception as e:
            print(f"批量创建排班记录失败: {e}")
            return False

    def delete_section(self, section_id: int) -> bool:
        """删除排班记录"""
        try:
            query = "DELETE FROM section WHERE sectionID = %s"
            result = self.execute_update(query, (section_id,))
            return result > 0
        except Exception as e:
            print(f"删除排班记录失败: {e}")
            return False

    def get_sections_by_date_range(self, start_date: str, end_date: str) -> List[Section]:
        """根据日期范围获取排班"""
        try:
            query = "SELECT * FROM section WHERE date BETWEEN %s AND %s ORDER BY date, timeslotID"
            results = self.execute_query(query, (start_date, end_date))
            return [Section.from_dict(row) for row in results] if results else []
        except Exception as e:
            print(f"获取日期范围排班失败: {e}")
            return []

    # ==================== 兼容性方法 ====================

    def update_appointment_quota(self, section_id: int) -> bool:
        """更新预约名额 - 内部使用（兼容性方法）"""
        return self.decrease_appointment_quota(section_id)

    def update_registration_quota(self, section_id: int) -> bool:
        """更新挂号名额 - 内部使用（兼容性方法）"""
        return self.decrease_registration_quota(section_id)