import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, Optional
from repository.base import Base

from model import Doctor
from model import DoctorDisplayView


class DoctorRepository(Base):
    def get_all_doctors(self) -> List[Doctor]:
        """获取所有医生基础信息"""
        query = "SELECT * FROM doctor"  
        results = self.execute_query(query)
        return [Doctor.from_dict(row) for row in results] if results else []

    def get_all_doctors_display(self) -> List[DoctorDisplayView]:
        """获取所有医生显示信息（使用视图）"""
        query = "SELECT * FROM doctor_display_view"
        results = self.execute_query(query)
        return [DoctorDisplayView.from_dict(row) for row in results] if results else []

    def get_doctor_by_id(self, doctor_id: int) -> Optional[Doctor]:
        """根据ID获取医生基础信息"""
        query = "SELECT * FROM doctor WHERE doctorID = %s"
        result = self.execute_query(query, (doctor_id,))
        return Doctor.from_dict(result[0]) if result else None

    def get_doctor_display_by_id(self, doctor_id: int) -> Optional[DoctorDisplayView]:
        """根据ID获取医生显示信息（使用视图）"""
        query = "SELECT * FROM doctor_display_view WHERE doctorID = %s"
        result = self.execute_query(query, (doctor_id,))
        return DoctorDisplayView.from_dict(result[0]) if result else None

    def get_doctors_by_office(self, office_id: int) -> List[Doctor]:
        """根据科室获取医生基础信息"""
        query = "SELECT * FROM doctor WHERE officeID = %s"
        results = self.execute_query(query, (office_id,))
        return [Doctor.from_dict(row) for row in results] if results else []

    def get_doctors_display_by_office(self, office_id: int) -> List[DoctorDisplayView]:
        """根据科室获取医生显示信息（使用视图）"""
        # 先通过 officeID 获取科室名称，然后用科室名称查询视图
        office_query = "SELECT name FROM office WHERE officeID = %s"
        office_result = self.execute_query(office_query, (office_id,))

        if not office_result:
            return []

        office_name = office_result[0]['name']
        query = "SELECT * FROM doctor_display_view WHERE office_name = %s"
        results = self.execute_query(query, (office_name,))
        return [DoctorDisplayView.from_dict(row) for row in results] if results else []

    def get_doctors_display_by_office_name(self, office_name: str) -> List[DoctorDisplayView]:
        """根据科室名称获取医生显示信息（使用视图）"""
        query = "SELECT * FROM doctor_display_view WHERE office_name = %s"
        results = self.execute_query(query, (office_name,))
        return [DoctorDisplayView.from_dict(row) for row in results] if results else []

    def update_doctor_patient_count(self, doctor_id: int, count: int) -> bool:
        """更新医生患者数量"""
        query = "UPDATE doctor SET NumberOfPatients = %s WHERE doctorID = %s"
        return self.execute_update(query, (count, doctor_id))

    def create_doctor(self, doctor: Doctor) -> bool:
        """创建医生"""
        query = """
        INSERT INTO doctor (name, age, expertiseID, officeID, positionID, NumberOfPatients) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        return self.execute_update(query, (
            doctor.name,
            doctor.age,
            doctor.expertiseID,
            doctor.officeID,
            doctor.positionID,
            doctor.NumberOfPatients
        ))

    def get_doctors_by_expertise(self, expertise_id: int) -> List[Doctor]:
        """根据专业领域获取医生基础信息"""
        query = "SELECT * FROM doctor WHERE expertiseID = %s"
        results = self.execute_query(query, (expertise_id,))
        return [Doctor.from_dict(row) for row in results] if results else []

    def get_doctors_display_by_expertise(self, expertise_name: str) -> List[DoctorDisplayView]:
        """根据专业领域名称获取医生显示信息（使用视图）"""
        query = "SELECT * FROM doctor_display_view WHERE expertise_name = %s"
        results = self.execute_query(query, (expertise_name,))
        return [DoctorDisplayView.from_dict(row) for row in results] if results else []