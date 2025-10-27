import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import Dict, List, Optional, Tuple
from repository.office import OfficeRepository
from repository.doctor import DoctorRepository
from repository.section import SectionRepository
from repository.registration import RegistrationRepository
from repository.timeslot import TimeslotRepository
from model import Office, Doctor, Section, Timeslot, Registration


class RegistrationService:
    """挂号业务逻辑服务"""

    def __init__(self):
        self.office_repo = OfficeRepository()
        self.doctor_repo = DoctorRepository()
        self.section_repo = SectionRepository()
        self.registration_repo = RegistrationRepository()
        self.timeslot_repo = TimeslotRepository()

    #输入时间，officeID，给出该section的挂号人数
    def get_current_timeslot_availability(self, office_id: int, datetime_str: str) -> Dict:
        try:
            # 解析日期和时间
            if ' ' in datetime_str:
                date_part, time_part = datetime_str.split(' ')
            else:
                date_part = datetime_str
                time_part = datetime_str

            # 查找当前时间段
            timeslot = self.timeslot_repo.get_timeslot_by_time(time_part)
            if not timeslot:
                all_timeslots = self.timeslot_repo.get_all_timeslots()
                return {
                    "error": "当前时间不在就诊时间段内",
                    "current_time": time_part,
                    "available_timeslots": [f"{ts.starttime}-{ts.endtime}" for ts in all_timeslots]
                }

            # 获取当前时间段的挂号名额信息
            availability_info = self.section_repo.get_current_timeslot_availability(
                office_id, date_part, timeslot.timeslotID
            )

            return {
                "timeslot": {
                    "timeslotID": timeslot.timeslotID,
                    "starttime": timeslot.starttime,
                    "endtime": timeslot.endtime
                },
                "availability": availability_info,
                "date": date_part
            }

        except Exception as e:
            print(f"获取当前时间段名额失败: {e}")
            return {"error": str(e)}

    #未预约患者挂号
    def register_without_appointment(self, patients_id: int, office_id: int, datetime_str: str) -> Tuple[bool, Optional[int]]:
        try:
            # 检查当前时间段可用性
            availability_info = self.get_current_timeslot_availability(office_id, datetime_str)
            if "error" in availability_info:
                return False, None

            availability = availability_info["availability"]
            if availability.get("restregistration", 0) <= 0:
                return False, None

            section_id = availability.get("sectionID")
            if not section_id:
                return False, None

            # 生成挂号号码
            current_registrations = self.registration_repo.get_registrations_by_section(section_id)
            number = len(current_registrations) + 1

            # 创建挂号记录
            success = self.registration_repo.create_registration(patients_id, section_id, number)
            if success:
                # 更新剩余挂号名额
                self.section_repo.decrease_registration_quota(section_id)
                return True, section_id
            else:
                return False, None

        except Exception as e:
            print(f"未预约患者挂号失败: {e}")
            return False, None

    def check_appointment_availability(self, section_id: int) -> dict:
        """检查排班预约可用性"""
        try:
            quota_info = self.section_repo.get_appointment_quota(section_id)
            return {
                "success": True,
                "section_id": section_id,
                "restappiontment": quota_info["restappiontment"],
                "appiontmentconvert": quota_info["appiontmentconvert"],
                "is_available": quota_info["restappiontment"] > 0
            }
        except Exception as e:
            print(f"检查预约可用性时出错: {e}")
            return {"success": False, "message": f"检查可用性失败: {str(e)}"}

    def register_with_appointment(self, patients_id: int, section_id: int) -> bool:
        """预约患者转挂号"""
        try:
            # 验证排班是否存在且有名额
            section = self.section_repo.get_section_by_id(section_id)
            if not section:
                return False

            if not self.section_repo.check_registration_availability(section_id):
                return False

            # 验证预约状态
            has_valid_appointment = self._check_appointment_status(patients_id, section_id)
            if not has_valid_appointment:
                print(f"患者 {patients_id} 没有排班 {section_id} 的有效预约")
                return False

            # 生成挂号号码
            current_registrations = self.registration_repo.get_registrations_by_section(section_id)
            number = len(current_registrations) + 1

            # 创建挂号记录
            success = self.registration_repo.create_registration(patients_id, section_id, number)
            if success:
                # 更新剩余挂号名额
                self.section_repo.decrease_registration_quota(section_id)
                # 标记预约为已完成
                self._complete_appointment(patients_id, section_id)
                return True
            return False

        except Exception as e:
            print(f"预约患者转挂号失败: {e}")
            return False

    #输入patientID和sectionId，输出挂号详情
    def get_registration_details(self, patients_id: int, section_id: int) -> Dict:
        try:
            registration_details = self.registration_repo.get_registration_details(patients_id, section_id)
            if not registration_details:
                return {"error": "未找到挂号信息"}

            return registration_details

        except Exception as e:
            print(f"获取挂号详情失败: {e}")
            return {"error": str(e)}

    #获取患者所有挂号信息
    def get_patient_registrations(self, patients_id: int) -> List[Dict]:
        try:
            return self.registration_repo.get_patient_registrations(patients_id)
        except Exception as e:
            print(f"获取患者挂号记录失败: {e}")
            return []

    # ==================== 辅助方法 ====================

    def _check_appointment_status(self, patients_id: int, section_id: int) -> bool:
        """验证患者是否有有效的预约"""
        try:
            # 创建预约服务实例
            from services.AppointmentService import AppointmentService
            appointment_service = AppointmentService()

            # 获取患者的所有预约
            appointment_result = appointment_service.get_patient_appointments(patients_id)

            if not appointment_result.get('success'):
                print(f"查询预约失败: {appointment_result.get('message')}")
                return False

            # 检查是否有该排班的有效预约
            appointments = appointment_result.get('appointments', [])
            valid_appointment = any(
                app.get('sectionID') == section_id and
                app.get('state') not in ['cancelled', 'completed']
                for app in appointments
            )

            return valid_appointment

        except Exception as e:
            print(f"检查预约状态失败: {e}")
            return False

    def _complete_appointment(self, patients_id: int, section_id: int) -> bool:
        """标记预约为已完成"""
        try:
            # 创建预约服务实例
            from services.appointment_service import AppointmentService
            appointment_service = AppointmentService()

            # 获取患者的所有预约
            appointment_result = appointment_service.get_patient_appointments(patients_id)

            if not appointment_result.get('success'):
                print(f"查询预约失败: {appointment_result.get('message')}")
                return False

            # 找到对应的预约记录
            appointments = appointment_result.get('appointments', [])
            target_appointment = None

            for app in appointments:
                if (app.get('sectionID') == section_id and
                        app.get('state') not in ['cancelled', 'completed']):
                    target_appointment = app
                    break

            if not target_appointment:
                print(f"未找到对应的有效预约: 患者{patients_id} 排班{section_id}")
                return False

            # 这里需要预约服务提供标记完成的方法
            # 由于当前AppointmentService没有标记完成的方法，暂时返回True
            # 实际应该调用: appointment_service.complete_appointment(target_appointment['appointmentID'])
            print(f"⚠️ 预约完成标记功能待实现: 预约ID {target_appointment.get('appointmentID')}")
            return True

        except Exception as e:
            print(f"标记预约完成失败: {e}")
            return False