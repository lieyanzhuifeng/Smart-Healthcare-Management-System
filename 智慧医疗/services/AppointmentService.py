# appointment_service.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, Optional
from model import Office, Doctor, Section, DoctorDisplayView
from repository.office import OfficeRepository
from repository.doctor import DoctorRepository
from repository.section import SectionRepository
from repository.appointment import AppointmentRepository

class AppointmentService:
    def __init__(self):
        self.office_repo = OfficeRepository()
        self.doctor_repo = DoctorRepository()
        self.section_repo = SectionRepository()
        self.appointment_repo = AppointmentRepository()

    # 获取所有科室
    def get_all_offices(self) -> List[Office]:
        try:
            return self.office_repo.get_all_offices()
        except Exception as e:
            print(f"获取科室列表时出错: {e}")
            return []

    # 根据科室获取医生列表（返回医生显示视图）
    def get_doctors_by_office(self, office_id: int) -> List[DoctorDisplayView]:
        try:
            return self.doctor_repo.get_doctors_display_by_office(office_id)
        except Exception as e:
            print(f"获取科室医生列表时出错: {e}")
            return []

    # 获取医生某天的排班信息
    def get_doctor_schedule_by_date(self, doctor_id: int, date: str) -> List[dict]:
        try:
            # 验证医生是否存在
            doctor = self.doctor_repo.get_doctor_by_id(doctor_id)
            if not doctor:
                print(f"医生ID {doctor_id} 不存在")
                return []
            return self.section_repo.get_doctor_schedule_by_date(doctor_id, date)
        except Exception as e:
            print(f"获取医生排班信息时出错: {e}")
            return []

    # 获取科室某天的排班信息
    def get_office_schedule_by_date(self, office_id: int, date: str) -> List[dict]:
        try:
            # 验证科室是否存在
            office = self.office_repo.get_office_by_id(office_id)
            if not office:
                print(f"科室ID {office_id} 不存在")
                return []
            return self.section_repo.get_office_schedule_by_date(office_id, date)
        except Exception as e:
            print(f"获取科室排班信息时出错: {e}")
            return []

    # 创建预约
    def create_appointment(self, patients_id: int, section_id: int) -> dict:
        try:
            # 验证排班是否存在
            section = self.section_repo.get_section_by_id(section_id)
            if not section:
                return {"success": False, "message": f"排班ID {section_id} 不存在"}
            # 检查排班是否还有预约名额
            quota_info = self.section_repo.get_appointment_quota(section_id)
            if quota_info["restappiontment"] <= 0:
                return {"success": False, "message": "该排班已无剩余预约名额"}
            # 检查是否已存在相同的有效预约
            if self.appointment_repo.check_appointment_exists(patients_id, section_id):
                return {"success": False, "message": "您已预约该排班，请勿重复预约"}
            # 创建预约
            success = self.appointment_repo.create_appointment(patients_id, section_id)
            if success:
                return {"success": True, "message": "预约成功", "section_id": section_id}
            else:
                return {"success": False, "message": "预约创建失败，请稍后重试"}
        except Exception as e:
            print(f"创建预约时出错: {e}")
            return {"success": False, "message": f"系统错误: {str(e)}"}

    # 取消预约
    def cancel_appointment(self, appointment_id: int) -> dict:
        try:
            # 验证预约是否存在
            appointment = self.appointment_repo.get_appointment_by_id(appointment_id)
            if not appointment:
                return {"success": False, "message": "未找到对应的预约记录"}
            # 检查预约状态
            if appointment['state'] == 3:  # 已取消状态
                return {"success": False, "message": "该预约已被取消"}
            # 取消预约
            success = self.appointment_repo.cancel_appointment(appointment_id)
            if success:
                return {"success": True, "message": "取消预约成功", "appointment_id": appointment_id}
            else:
                return {"success": False, "message": "取消预约失败，请稍后重试"}
        except Exception as e:
            print(f"取消预约时出错: {e}")
            return {"success": False, "message": f"系统错误: {str(e)}"}

    # 获取患者所有预约信息
    def get_patient_appointments(self, patients_id: int) -> dict:
        try:
            # 获取所有预约记录
            appointments = self.appointment_repo.get_patient_appointments(patients_id)
            # 获取有效预约（用于统计）
            active_appointments = self.appointment_repo.get_active_appointments_by_patient(patients_id)
            # 统计信息
            stats = {
                "total": len(appointments),
                "active": len(active_appointments),
                "cancelled": len([a for a in appointments if a.get('state') == 'cancelled']),
                "completed": len([a for a in appointments if a.get('state') == 'completed'])
            }
            return {"success": True, "appointments": appointments, "statistics": stats}
        except Exception as e:
            print(f"获取患者预约信息时出错: {e}")
            return {
                "success": False,
                "message": f"获取预约信息失败: {str(e)}",
                "appointments": [],
                "statistics": {"total": 0, "active": 0, "cancelled": 0, "completed": 0}
            }

    # 获取科室某天有排班的医生及其排班信息（分组显示）
    def get_available_doctors_by_date_and_office(self, office_id: int, date: str) -> List[dict]:
        try:
            # 获取科室排班信息
            office_schedule = self.get_office_schedule_by_date(office_id, date)
            if not office_schedule:
                return []
            # 按医生分组
            doctors_schedule = {}
            for schedule in office_schedule:
                doctor_id = schedule.get('doctorID')
                if doctor_id not in doctors_schedule:
                    # 获取医生详细信息
                    doctor_info = {
                        'doctorID': doctor_id,
                        'doctor_name': schedule.get('doctor_name'),
                        'office_name': schedule.get('office_name'),
                        'expertise_name': schedule.get('expertise_name'),
                        'position_name': schedule.get('position_name')
                    }
                    doctors_schedule[doctor_id] = {'doctor_info': doctor_info, 'schedules': []}
                # 添加排班信息
                schedule_info = {
                    'sectionID': schedule.get('sectionID'),
                    'starttime': schedule.get('starttime'),
                    'endtime': schedule.get('endtime'),
                    'restappiontment': schedule.get('restappiontment')
                }
                doctors_schedule[doctor_id]['schedules'].append(schedule_info)
            return list(doctors_schedule.values())
        except Exception as e:
            print(f"获取可用医生排班信息时出错: {e}")
            return []

    # 检查排班预约可用性
    def check_appointment_availability(self, section_id: int) -> dict:
        try:
            quota_info = self.section_repo.get_appointment_quota(section_id)
            section = self.section_repo.get_section_by_id(section_id)
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

    # 在AppointmentService类中添加
    def complete_appointment(self, appointment_id: int) -> dict:
        """标记预约为已完成"""
        try:
            # 验证预约是否存在
            appointment = self.appointment_repo.get_appointment_by_id(appointment_id)
            if not appointment:
                return {"success": False, "message": "未找到对应的预约记录"}

            # 更新预约状态为已完成
            # 这里需要AppointmentRepository有更新状态的方法
            success = self.appointment_repo.update_appointment_state(appointment_id, "completed")

            if success:
                return {"success": True, "message": "预约已完成", "appointment_id": appointment_id}
            else:
                return {"success": False, "message": "更新预约状态失败"}

        except Exception as e:
            print(f"完成预约时出错: {e}")
            return {"success": False, "message": f"系统错误: {str(e)}"}