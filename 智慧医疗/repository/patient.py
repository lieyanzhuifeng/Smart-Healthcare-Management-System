import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mysql.connector
from mysql.connector import Error
from typing import List, Optional, Dict
from model import Patients, Doctor, Expertise, Office, Position, Information, Medicine, OrderForMedicine, Pharmacy, Registration, Room, Section, Timeslot, Appointment
from repository.base import Base

class PatientRepository(Base):
    def get_all_patients(self) -> List[Patients]:
        """获取所有患者"""
        query = "SELECT * FROM patients"
        results = self.execute_query(query)
        return [Patients.from_dict(row) for row in results] if results else []

    def get_patient_by_id(self, patient_id: int) -> Optional[Patients]:
        """根据ID获取患者"""
        query = "SELECT * FROM patients WHERE patientsID = %s"
        result = self.execute_query(query, (patient_id,))
        return Patients.from_dict(result[0]) if result else None

    def create_patient(self, name: str, age: int) -> bool:
        """创建新患者"""
        query = "INSERT INTO patients (name, age) VALUES (%s, %s)"
        return self.execute_update(query, (name, age))

    def update_patient(self, patient_id: int, name: str, age: int) -> bool:
        """更新患者信息"""
        query = "UPDATE patients SET name = %s, age = %s WHERE patientsID = %s"
        return self.execute_update(query, (name, age, patient_id))

    def delete_patient(self, patient_id: int) -> bool:
        """删除患者"""
        query = "DELETE FROM patients WHERE patientsID = %s"
        return self.execute_update(query, (patient_id,))

    def search_patients_by_name(self, name: str) -> List[Patients]:
        """根据姓名搜索患者"""
        query = "SELECT * FROM patients WHERE name LIKE %s"
        results = self.execute_query(query, (f"%{name}%",))
        return [Patients.from_dict(row) for row in results] if results else []

    def get_patients_by_age_range(self, min_age: int, max_age: int) -> List[Patients]:
        """根据年龄范围获取患者"""
        query = "SELECT * FROM patients WHERE age BETWEEN %s AND %s"
        results = self.execute_query(query, (min_age, max_age))
        return [Patients.from_dict(row) for row in results] if results else []