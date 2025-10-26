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

    #预约患者转挂号
    def register_with_appointment(self, patients_id: int, section_id: int) -> bool:
        try:
            # 验证排班是否存在且有名额
            section = self.section_repo.get_section_by_id(section_id)
            if not section:
                return False

            if not self.section_repo.check_registration_availability(section_id):
                return False

            # 这里需要调用预约服务来验证预约状态
            # has_valid_appointment = self._check_appointment_status(patients_id, section_id)
            # if not has_valid_appointment:
            #     return False

            # 生成挂号号码
            current_registrations = self.registration_repo.get_registrations_by_section(section_id)
            number = len(current_registrations) + 1

            # 创建挂号记录
            success = self.registration_repo.create_registration(patients_id, section_id, number)
            if success:
                # 更新剩余挂号名额
                self.section_repo.decrease_registration_quota(section_id)
                # 标记预约为已完成（需要预约服务的配合）
                # self._complete_appointment(patients_id, section_id)
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

    # 验证患者是否有有效的预约（需要与预约服务交互）
    def _check_appointment_status(self, patients_id: int, section_id: int) -> bool:
        # 这里应该调用预约服务的接口
        # 暂时返回True用于测试
        return True

    # 标记预约为已完成（需要与预约服务交互）
    def _complete_appointment(self, patients_id: int, section_id: int) -> bool:
        # 这里应该调用预约服务的接口
        # 暂时返回True用于测试
        return True