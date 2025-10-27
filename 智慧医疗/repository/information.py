import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from repository.base import Base
from model import DoctorDisplayView, Medicine, OrderForMedicine

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class MedicalRecordView:
    """病历视图模型"""
    infID: int
    time: datetime
    information: str
    have_medicine: bool
    doctor: DoctorDisplayView

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            infID=data.get('infID'),
            time=data.get('time'),
            information=data.get('information'),
            have_medicine=data.get('have_medicine'),
            doctor=data.get('doctor')
        )


class InformationRepository(Base):
    def get_patient_medical_records(self, patients_id: int) -> List[MedicalRecordView]:
        """获取患者病历 - 对应需求13"""
        query = """
                SELECT i.infID, i.time, i.information, i.have_medicine,
                       d.doctorID, d.name as doctor_name, d.age, 
                       o.name as office_name, e.name as expertise_name, 
                       p.name as position_name, d.NumberOfPatients
                FROM information i
                JOIN doctor d ON i.doctorID = d.doctorID
                JOIN office o ON d.officeID = o.officeID
                JOIN expertise e ON d.expertiseID = e.expertiseID
                JOIN position p ON d.positionID = p.positionID
                WHERE i.patientsID = %s
                ORDER BY i.time DESC
                """

        try:
            # 使用 Base 类提供的 execute_query 方法
            results = self.execute_query(query, (patients_id,))

            medical_records = []
            for row in results:
                doctor_display = DoctorDisplayView(
                    doctorID=row['doctorID'],
                    doctor_name=row['doctor_name'],
                    age=row['age'],
                    office_name=row['office_name'],
                    expertise_name=row['expertise_name'],
                    position_name=row['position_name'],
                    NumberOfPatients=row['NumberOfPatients']
                )

                medical_record = MedicalRecordView(
                    infID=row['infID'],
                    time=row['time'],
                    information=row['information'],
                    have_medicine=bool(row['have_medicine']),
                    doctor=doctor_display
                )
                medical_records.append(medical_record)

            return medical_records

        except Exception as e:
            print(f"获取患者病历时出错: {e}")
            return []

    def get_prescription_details(self, inf_id: int) -> List[dict]:
        """获取处方详情 - 对应需求14"""
        query = """
                SELECT m.medicineID, m.name, m.price, m.description, 
                       o.amount, o.price as total_price, o.orderID
                FROM order_for_medicine o
                         JOIN medicine m ON o.medicineID = m.medicineID
                WHERE o.infID = %s
                """

        try:
            # 使用 Base 类提供的 execute_query 方法
            results = self.execute_query(query, (inf_id,))

            # 转换为字典列表，包含 Medicine 和 OrderForMedicine 对象
            prescription_details = []
            for row in results:
                medicine = Medicine(
                    medicineID=row['medicineID'],
                    name=row['name'],
                    price=float(row['price']),
                    description=row['description']
                )

                order = OrderForMedicine(
                    orderID=row['orderID'],
                    infID=inf_id,
                    medicineID=row['medicineID'],
                    amount=row['amount'],
                    price=float(row['total_price'])
                )

                detail = {
                    'medicine': medicine,
                    'order': order
                }
                prescription_details.append(detail)

            return prescription_details

        except Exception as e:
            print(f"获取处方详情时出错: {e}")
            return []