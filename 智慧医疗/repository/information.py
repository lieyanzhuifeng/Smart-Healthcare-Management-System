import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from repository.base import Base
from repository.registration import RegistrationRepository
from model import DoctorDisplayView, Medicine, OrderForMedicine

from dataclasses import dataclass
from datetime import datetime
from typing import List
from model import Registration

@dataclass
class MedicalRecordView:
    """病历视图模型"""
    registrationID: int
    time: datetime
    information: str
    have_medicine: bool
    doctor: DoctorDisplayView

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            registrationID=data.get('registrationID'),
            time=data.get('time'),
            information=data.get('information'),
            have_medicine=data.get('have_medicine'),
            doctor=data.get('doctor')
        )


class InformationRepository(Base):
    def __init__(self):
        super().__init__()
        self.registration_repo = RegistrationRepository()  # 在这里初始化

    def get_patient_medical_records(self, patients_id: int) -> List[MedicalRecordView]:
        """获取患者病历 - 对应需求13"""
        query = """
                SELECT i.registrationID, i.time, i.information, i.have_medicine,
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
                    registrationID=row['registrationID'],
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

    def get_prescription_details(self, registration_id: int) -> List[dict]:
        """获取处方详情 - 对应需求14"""
        query = """
                SELECT m.medicineID, m.name, m.price, m.description, 
                       o.amount, o.price as total_price, o.orderID
                FROM order_for_medicine o
                         JOIN medicine m ON o.medicineID = m.medicineID
                WHERE o.registrationID = %s
                """

        try:
            # 使用 Base 类提供的 execute_query 方法
            results = self.execute_query(query, (registration_id,))

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
                    registrationID=registration_id,
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

    # 为挂号编写就诊记录
    def create_medical_record(self, registration_id: int, information: str, doctor_id: int,
                              have_medicine: bool) -> bool:
        try:
            # 首先通过registration_repo获取患者ID
            registration_info = self.registration_repo.get_registration_by_id(registration_id)
            if not registration_info:
                print(f"挂号记录 {registration_id} 不存在")
                return False

            patients_id = registration_info['patientsID']

            # 插入就诊记录到information表
            query = """
                   INSERT INTO information (registrationID, doctorID, patientsID, time, have_medicine, information) 
                   VALUES (%s, %s, %s, NOW(), %s, %s)
               """
            result = self.execute_update(query, (registration_id, doctor_id, patients_id, have_medicine, information))

            if result > 0:
                print(f"就诊记录插入成功，挂号ID: {registration_id}")

                # 如果不开药，直接将挂号状态改为4（已取药）
                if not have_medicine:
                    update_success = self.registration_repo.update_registration_state(registration_id,
                                                                                      Registration.STATE_MEDICINE_TAKEN)
                    if update_success:
                        print(f"未开药，挂号 {registration_id} 状态已更新为已取药")
                    else:
                        print(f"未开药，但挂号 {registration_id} 状态更新失败")
                    return update_success
                # 如果开药，状态保持为就诊中，等待调用开药函数
                else:
                    print(f"已记录需要开药，请调用开药函数为挂号 {registration_id} 开药")
                    return True
            else:
                print("就诊记录插入失败")
                return False

        except Exception as e:
            print(f"创建就诊记录失败: {e}")
            return False