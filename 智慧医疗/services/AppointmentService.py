# appointment_service.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Optional
from model import Office, Doctor, Section,DoctorDisplayView
from repository.office import OfficeRepository
from repository.doctor import DoctorRepository
from repository.section import SectionRepository


class AppointmentService:
    def __init__(self):
        self.office_repo = OfficeRepository()
        self.doctor_repo = DoctorRepository()
        self.section_repo = SectionRepository()

    def get_all_offices(self) -> List[Office]:
        """获取所有科室"""
        try:
            return self.office_repo.get_all_offices()
        except Exception as e:
            # 这里可以添加日志记录
            print(f"获取科室列表时出错: {e}")
            return []

    def get_doctors_by_office(self, office_id: int) -> List[DoctorDisplayView]:
        """
        根据科室获取医生列表 （返回医生显示视图）
        """
        try:
            return self.doctor_repo.get_doctors_display_by_office(office_id)
        except Exception as e:
            print(f"获取科室医生列表时出错: {e}")
            return []

    def get_doctor_schedule_by_date(self, doctor_id: int, date: str) -> List[dict]:
        """
        获取医生某天的排班信息 - 对应需求3
        需求3：查询医生某天的排班信息（包括时间段和剩余预约名额）

        Args:
            doctor_id: 医生ID
            date: 日期字符串，格式为'YYYY-MM-DD'

        Returns:
            List[dict]: 排班信息列表，包含sectionID、starttime、endtime、restappiontment等字段
        """
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

    def get_office_schedule_by_date(self, office_id: int, date: str) -> List[dict]:
        """
        获取科室某天的排班信息 - 对应需求4
        需求4：查询科室某天的排班医生信息（包括医生信息和剩余预约名额）

        Args:
            office_id: 科室ID
            date: 日期字符串，格式为'YYYY-MM-DD'

        Returns:
            List[dict]: 排班信息列表，包含医生信息和排班详情
        """
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
