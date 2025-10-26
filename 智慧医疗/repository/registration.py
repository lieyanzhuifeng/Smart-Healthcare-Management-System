import mysql.connector
from mysql.connector import Error, pooling
from typing import List, Optional, Type, TypeVar, Any, Dict, Union
from abc import ABC
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from repository.base import Base

class RegistrationRepository(Base):
    def create_registration(self, patients_id: int, section_id: int, number: int) -> bool:
        """创建挂号 - 对应需求9,10"""
        try:
            # 使用状态值0表示"已挂号/待就诊"
            query = "INSERT INTO registration (patientsID, sectionID, number, state) VALUES (%s, %s, %s, 0)"
            result = self.execute_update(query, (patients_id, section_id, number))
            return result > 0
        except Exception as e:
            print(f"创建挂号记录失败: {e}")
            return False

    def get_registration_details(self, patients_id: int, section_id: int) -> Optional[dict]:
        """获取挂号详情 - 对应需求11"""
        try:
            query = """
                    SELECT d.*, r.number, s.roomID, r.state
                    FROM registration r
                             JOIN section s ON r.sectionID = s.sectionID
                             JOIN doctor d ON s.doctorID = d.doctorID
                    WHERE r.patientsID = %s
                      AND r.sectionID = %s
                    """
            results = self.execute_query(query, (patients_id, section_id))
            return results[0] if results else None
        except Exception as e:
            print(f"获取挂号详情失败: {e}")
            return None

    def get_patient_registrations(self, patients_id: int) -> List[dict]:
        """获取患者所有挂号信息 - 对应需求12"""
        try:
            query = """
                    SELECT d.*, r.number, s.roomID, r.state, s.date, t.starttime, t.endtime
                    FROM registration r
                             JOIN section s ON r.sectionID = s.sectionID
                             JOIN doctor d ON s.doctorID = d.doctorID
                             JOIN timeslot t ON s.timeslotID = t.timeslotID
                    WHERE r.patientsID = %s
                    ORDER BY s.date DESC, t.starttime DESC
                    """
            return self.execute_query(query, (patients_id,))
        except Exception as e:
            print(f"获取患者挂号信息失败: {e}")
            return []

    def get_registrations_by_section(self, section_id: int) -> List[dict]:
        """根据排班获取所有挂号记录"""
        try:
            query = "SELECT * FROM registration WHERE sectionID = %s"
            return self.execute_query(query, (section_id,))
        except Exception as e:
            print(f"获取排班挂号记录失败: {e}")
            return []

    def update_registration_state(self, registration_id: int, state: int) -> bool:
        """更新挂号状态"""
        try:
            # 状态: 0=已挂号/待就诊, 1=就诊中, 2=已就诊, 3=已取消
            query = "UPDATE registration SET state = %s WHERE registrationID = %s"
            result = self.execute_update(query, (state, registration_id))
            return result > 0
        except Exception as e:
            print(f"更新挂号状态失败: {e}")
            return False

    def get_registration_by_id(self, registration_id: int) -> Optional[dict]:
        """根据ID获取挂号信息"""
        try:
            query = "SELECT * FROM registration WHERE registrationID = %s"
            results = self.execute_query(query, (registration_id,))
            return results[0] if results else None
        except Exception as e:
            print(f"获取挂号信息失败: {e}")
            return None

    def delete_registration(self, registration_id: int) -> bool:
        """删除挂号记录"""
        try:
            query = "DELETE FROM registration WHERE registrationID = %s"
            result = self.execute_update(query, (registration_id,))
            return result > 0
        except Exception as e:
            print(f"删除挂号记录失败: {e}")
            return False

    def get_registration_by_patient_and_section(self, patients_id: int, section_id: int) -> Optional[dict]:
        """根据患者和排班获取挂号记录"""
        try:
            query = "SELECT * FROM registration WHERE patientsID = %s AND sectionID = %s"
            results = self.execute_query(query, (patients_id, section_id))
            return results[0] if results else None
        except Exception as e:
            print(f"获取患者排班挂号记录失败: {e}")
            return None