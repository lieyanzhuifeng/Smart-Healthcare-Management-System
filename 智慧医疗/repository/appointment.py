import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, Optional
from repository.base import Base
from repository.section import SectionRepository
from model import Appointment  # 导入Appointment类来使用状态常量

class AppointmentRepository(Base):
    def __init__(self):
        super().__init__()
        self.section_repo = SectionRepository()  # 在这里初始化

    def create_appointment(self, patients_id: int, section_id: int) -> bool:
        """创建预约 - 对应需求5"""
        # 首先检查是否还有预约名额
        quota_info = self.section_repo.get_appointment_quota(section_id)

        if quota_info["restappiontment"] <= 0:
            print(f"排班 {section_id} 没有剩余预约名额")
            return False

        # 检查是否已存在相同的有效预约
        if self.check_appointment_exists(patients_id, section_id):
            print(f"患者 {patients_id} 已存在排班 {section_id} 的有效预约")
            return False

        try:
            # 使用事务上下文管理器
            with self.transaction():
                # 创建预约记录，状态为有效 (1)
                appointment_query = "INSERT INTO appointment (patientsID, sectionID, state) VALUES (%s, %s, %s)"
                result1 = self.execute_update(appointment_query, (patients_id, section_id, 1))

                if result1 <= 0:
                    raise Exception("创建预约记录失败")

                # 减少预约名额
                quota_query = "UPDATE section SET restappiontment = restappiontment - 1 WHERE sectionID = %s AND restappiontment > 0"
                result2 = self.execute_update(quota_query, (section_id,))

                if result2 <= 0:
                    raise Exception("减少预约名额失败")

                # 增加预约转挂号预留人数
                if not self.section_repo.increase_appointment_convert(section_id):
                    raise Exception("增加预约转挂号预留人数失败")

                print(f"成功创建预约: 患者 {patients_id}, 排班 {section_id}")
                return True

        except Exception as e:
            print(f"创建预约失败: {e}")
            return False

    def cancel_appointment(self, appointment_id: int) -> bool:
        """取消预约 - 对应需求6"""
        # 首先根据appointmentID获取预约信息
        appointment = self.get_appointment_by_id(appointment_id)
        if not appointment:
            print(f"预约ID {appointment_id} 不存在")
            return False

        # 检查预约状态：只有状态为1（有效且未转挂号）才能取消
        if appointment['state'] != 1:
            print(f"预约 {appointment_id} 状态为{appointment['state']}，不能取消（只有状态为1的有效预约才能取消）")
            return False

        patients_id = appointment['patientsID']
        section_id = appointment['sectionID']

        try:
            # 使用事务上下文管理器
            with self.transaction():
                # 取消预约，状态改为已取消 (3)
                appointment_query = "UPDATE appointment SET state = %s WHERE appointmentID = %s"
                result1 = self.execute_update(appointment_query, (3, appointment_id))

                if result1 <= 0:
                    raise Exception("取消预约失败")

                # 恢复预约名额
                quota_query = "UPDATE section SET restappiontment = restappiontment + 1 WHERE sectionID = %s"
                result2 = self.execute_update(quota_query, (section_id,))

                if result2 <= 0:
                    raise Exception("恢复预约名额失败")

                # 减少预约转挂号预留人数
                if not self.section_repo.decrease_appointment_convert(section_id):
                    raise Exception("减少预约转挂号预留人数失败")

                print(f"成功取消预约: 预约ID {appointment_id}, 患者 {patients_id}, 排班 {section_id}")
                return True

        except Exception as e:
            print(f"取消预约失败: {e}")
            return False

    def get_patient_appointments(self, patients_id: int) -> List[dict]:
        """获取患者所有预约信息 - 对应需求7"""
        query = """
                SELECT a.appointmentID, \
                       a.patientsID, \
                       a.sectionID, \
                       a.state, -- 添加了 a.patientsID
                       d.doctorID, \
                       d.name as doctor_name, \
                       d.age,
                       o.name as office_name, \
                       e.name as expertise_name, \
                       p.name as position_name,
                       s.date, \
                       t.starttime, \
                       t.endtime, \
                       s.restappiontment
                FROM appointment a
                         JOIN section s ON a.sectionID = s.sectionID
                         JOIN doctor d ON s.doctorID = d.doctorID
                         JOIN office o ON d.officeID = o.officeID
                         JOIN expertise e ON d.expertiseID = e.expertiseID
                         JOIN position p ON d.positionID = p.positionID
                         JOIN timeslot t ON s.timeslotID = t.timeslotID
                WHERE a.patientsID = %s
                ORDER BY s.date, t.starttime
                """
        try:
            results = self.execute_query(query, (patients_id,))
            return results if results else []
        except Exception as e:
            print(f"获取患者预约信息失败: {e}")
            return []

    def get_appointment_by_id(self, appointment_id: int) -> Optional[dict]:
        """根据预约ID获取预约信息"""
        query = "SELECT * FROM appointment WHERE appointmentID = %s"
        try:
            result = self.execute_query(query, (appointment_id,))
            return result[0] if result else None
        except Exception as e:
            print(f"获取预约信息失败: {e}")
            return None

    def get_appointment_by_patient_and_section(self, patients_id: int, section_id: int) -> Optional[dict]:
        """根据患者ID和排班ID获取预约信息"""
        query = "SELECT * FROM appointment WHERE patientsID = %s AND sectionID = %s"
        try:
            result = self.execute_query(query, (patients_id, section_id))
            return result[0] if result else None
        except Exception as e:
            print(f"获取预约信息失败: {e}")
            return None

    def update_appointment_state(self, appointment_id: int, state: int) -> bool:
        """更新预约状态"""
        query = "UPDATE appointment SET state = %s WHERE appointmentID = %s"
        try:
            result = self.execute_update(query, (state, appointment_id))
            return result > 0
        except Exception as e:
            print(f"更新预约状态失败: {e}")
            return False

    def get_active_appointments_by_patient(self, patients_id: int) -> List[dict]:
        """获取患者的有效预约（有效状态）"""
        query = """
                SELECT a.appointmentID, a.sectionID, a.state,
                       d.name as doctor_name, o.name as office_name,
                       s.date, t.starttime, t.endtime
                FROM appointment a
                         JOIN section s ON a.sectionID = s.sectionID
                         JOIN doctor d ON s.doctorID = d.doctorID
                         JOIN office o ON d.officeID = o.officeID
                         JOIN timeslot t ON s.timeslotID = t.timeslotID
                WHERE a.patientsID = %s AND a.state = %s
                ORDER BY s.date, t.starttime
                """
        try:
            results = self.execute_query(query, (patients_id, Appointment.STATE_ACTIVE))
            return results if results else []
        except Exception as e:
            print(f"获取患者有效预约失败: {e}")
            return []

    def check_appointment_exists(self, patients_id: int, section_id: int) -> bool:
        """检查是否已存在相同的有效预约"""
        query = "SELECT COUNT(*) as count FROM appointment WHERE patientsID = %s AND sectionID = %s AND state = %s"
        try:
            result = self.execute_query(query, (patients_id, section_id, Appointment.STATE_ACTIVE))
            return result[0]['count'] > 0 if result else False
        except Exception as e:
            print(f"检查预约是否存在失败: {e}")
            return False

    def get_appointment_count_by_section(self, section_id: int) -> int:
        """获取某个排班的预约数量"""
        query = "SELECT COUNT(*) as count FROM appointment WHERE sectionID = %s AND state = %s"
        try:
            result = self.execute_query(query, (section_id, Appointment.STATE_ACTIVE))
            return result[0]['count'] if result else 0
        except Exception as e:
            print(f"获取排班预约数量失败: {e}")
            return 0

    def complete_appointment(self, appointment_id: int) -> bool:
        """完成预约"""
        query = "UPDATE appointment SET state = %s WHERE appointmentID = %s"
        try:
            result = self.execute_update(query, (Appointment.STATE_COMPLETED, appointment_id))
            return result > 0
        except Exception as e:
            print(f"完成预约失败: {e}")
            return False

    def get_appointments_by_state(self, state: int) -> List[dict]:
        """根据状态获取预约列表"""
        query = "SELECT * FROM appointment WHERE state = %s"
        try:
            results = self.execute_query(query, (state,))
            return results if results else []
        except Exception as e:
            print(f"获取状态为 {state} 的预约失败: {e}")
            return []

    def get_appointment_state_description(self, state: int) -> str:
        """获取状态描述"""
        return Appointment.STATE_DESCRIPTIONS.get(state, "未知状态")