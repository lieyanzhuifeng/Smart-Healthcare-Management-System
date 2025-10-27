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
from model import Registration  # 导入Registration类来使用状态常量

class RegistrationRepository(Base):
    # 创建挂号
    def create_registration(self, patients_id: int, section_id: int, number: int) -> bool:
        try:
            query = "INSERT INTO registration (patientsID, sectionID, number, state) VALUES (%s, %s, %s, %s)"
            result = self.execute_update(query, (patients_id, section_id, number, Registration.STATE_REGISTERED))
            return result > 0
        except Exception as e:
            print(f"创建挂号记录失败: {e}")
            return False

    # 获取挂号详情
    def get_registration_details(self, patients_id: int, section_id: int) -> Optional[dict]:
        try:
            query = "SELECT r.*, d.*, s.roomID, s.date, t.starttime, t.endtime FROM registration r JOIN section s ON r.sectionID = s.sectionID JOIN doctor d ON s.doctorID = d.doctorID JOIN timeslot t ON s.timeslotID = t.timeslotID WHERE r.patientsID = %s AND r.sectionID = %s"
            results = self.execute_query(query, (patients_id, section_id))
            return results[0] if results else None
        except Exception as e:
            print(f"获取挂号详情失败: {e}")
            return None

    # 获取患者所有挂号信息
    def get_patient_registrations(self, patients_id: int) -> List[dict]:
        try:
            query = "SELECT r.*, d.*, s.roomID, s.date, t.starttime, t.endtime, o.name as office_name, e.name as expertise_name, p.name as position_name FROM registration r JOIN section s ON r.sectionID = s.sectionID JOIN doctor d ON s.doctorID = d.doctorID JOIN office o ON d.officeID = o.officeID JOIN expertise e ON d.expertiseID = e.expertiseID JOIN position p ON d.positionID = p.positionID JOIN timeslot t ON s.timeslotID = t.timeslotID WHERE r.patientsID = %s ORDER BY s.date DESC, t.starttime DESC"
            return self.execute_query(query, (patients_id,))
        except Exception as e:
            print(f"获取患者挂号信息失败: {e}")
            return []

    # 根据排班获取所有挂号记录
    def get_registrations_by_section(self, section_id: int) -> List[dict]:
        try:
            query = "SELECT * FROM registration WHERE sectionID = %s ORDER BY number"
            return self.execute_query(query, (section_id,))
        except Exception as e:
            print(f"获取排班挂号记录失败: {e}")
            return []

    # 更新挂号状态
    def update_registration_state(self, registration_id: int, state: int) -> bool:
        try:
            query = "UPDATE registration SET state = %s WHERE registrationID = %s"
            result = self.execute_update(query, (state, registration_id))
            return result > 0
        except Exception as e:
            print(f"更新挂号状态失败: {e}")
            return False

    # 根据ID获取挂号信息
    def get_registration_by_id(self, registration_id: int) -> Optional[dict]:
        try:
            query = "SELECT * FROM registration WHERE registrationID = %s"
            results = self.execute_query(query, (registration_id,))
            return results[0] if results else None
        except Exception as e:
            print(f"获取挂号信息失败: {e}")
            return None

    # 删除挂号记录
    def delete_registration(self, registration_id: int) -> bool:
        try:
            query = "DELETE FROM registration WHERE registrationID = %s"
            result = self.execute_update(query, (registration_id,))
            return result > 0
        except Exception as e:
            print(f"删除挂号记录失败: {e}")
            return False

    # 根据患者和排班获取挂号记录
    def get_registration_by_patient_and_section(self, patients_id: int, section_id: int) -> Optional[dict]:
        try:
            query = "SELECT * FROM registration WHERE patientsID = %s AND sectionID = %s"
            results = self.execute_query(query, (patients_id, section_id))
            return results[0] if results else None
        except Exception as e:
            print(f"获取患者排班挂号记录失败: {e}")
            return None

    # 根据状态获取挂号记录
    def get_registrations_by_state(self, state: int) -> List[dict]:
        try:
            query = "SELECT * FROM registration WHERE state = %s ORDER BY registrationID"
            return self.execute_query(query, (state,))
        except Exception as e:
            print(f"获取状态为 {state} 的挂号记录失败: {e}")
            return []

    # 获取患者的有效挂号记录（非取消状态）
    def get_active_registrations_by_patient(self, patients_id: int) -> List[dict]:
        try:
            query = "SELECT r.*, d.name as doctor_name, o.name as office_name, s.date, t.starttime, t.endtime FROM registration r JOIN section s ON r.sectionID = s.sectionID JOIN doctor d ON s.doctorID = d.doctorID JOIN office o ON d.officeID = o.officeID JOIN timeslot t ON s.timeslotID = t.timeslotID WHERE r.patientsID = %s AND r.state != %s ORDER BY s.date, t.starttime"
            return self.execute_query(query, (patients_id, Registration.STATE_CANCELLED))
        except Exception as e:
            print(f"获取患者有效挂号记录失败: {e}")
            return []

    # 取消挂号
    def cancel_registration(self, registration_id: int) -> bool:
        try:
            query = "UPDATE registration SET state = %s WHERE registrationID = %s AND state = %s"
            result = self.execute_update(query, (Registration.STATE_CANCELLED, registration_id, Registration.STATE_REGISTERED))
            return result > 0
        except Exception as e:
            print(f"取消挂号失败: {e}")
            return False

    # 获取某个排班的挂号数量
    def get_registration_count_by_section(self, section_id: int) -> int:
        try:
            query = "SELECT COUNT(*) as count FROM registration WHERE sectionID = %s AND state != %s"
            result = self.execute_query(query, (section_id, Registration.STATE_CANCELLED))
            return result[0]['count'] if result else 0
        except Exception as e:
            print(f"获取排班挂号数量失败: {e}")
            return 0

    # 获取状态描述
    def get_registration_state_description(self, state: int) -> str:
        return Registration.STATE_DESCRIPTIONS.get(state, "未知状态")