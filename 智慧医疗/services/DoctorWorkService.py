import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List

from repository.information import InformationRepository
from repository.medicine import MedicalOrderRepository, MedicineRepository
from repository.registration import RegistrationRepository
from model import Medicine

class DoctorWorkService:
    """医生工作服务类，协调调用各个仓库的函数"""

    def __init__(self):
        self.registration_repo = RegistrationRepository()
        self.information_repo = InformationRepository()
        self.medical_order_repo = MedicalOrderRepository()
        self.medicine_repo = MedicineRepository()

    def get_doctor_daily_schedule(self, doctor_id: int, date: str) -> List[dict]:
        """
        获取医生某天的所有有效挂号信息

        Args:
            doctor_id: 医生ID
            date: 日期 (YYYY-MM-DD)

        Returns:
            List[dict]: 挂号信息和患者信息列表
        """
        return self.registration_repo.get_active_registrations_by_doctor_and_date(doctor_id, date)

    def start_patient_visit(self, registration_id: int) -> bool:
        """
        开始患者就诊（将挂号状态改为就诊中）

        Args:
            registration_id: 挂号ID

        Returns:
            bool: 操作是否成功
        """
        return self.registration_repo.start_medical_visit(registration_id)

    def create_patient_medical_record(self, registration_id: int, information: str,
                                      doctor_id: int, have_medicine: bool) -> bool:
        """
        创建患者就诊记录

        Args:
            registration_id: 挂号ID
            information: 病历内容
            doctor_id: 医生ID
            have_medicine: 是否开药

        Returns:
            bool: 操作是否成功
        """
        return self.information_repo.create_medical_record(registration_id, information, doctor_id, have_medicine)

    def prescribe_medicines(self, registration_id: int, medicine_orders: List[dict]) -> bool:
        """
        为患者开药

        Args:
            registration_id: 挂号ID
            medicine_orders: 药品订单列表

        Returns:
            bool: 操作是否成功
        """
        return self.medical_order_repo.prescribe_medicine(registration_id, medicine_orders)

    def get_all_medicines(self) -> List[Medicine]:
        """
        获取所有药品信息

        Returns:
            List[Medicine]: 药品对象列表
        """
        return self.medicine_repo.get_all_medicines()

    def get_medicines_for_prescription(self) -> List[dict]:
        """
        获取用于开药界面的药品信息（简化版）

        Returns:
            List[dict]: 包含药品ID和名称的字典列表
        """
        medicines = self.get_all_medicines()
        return [
            {
                "medicineID": medicine.medicineID,
                "name": medicine.name,
                "price": medicine.price,
                "description": medicine.description
            }
            for medicine in medicines
        ]

    def complete_patient_visit(self, registration_id: int, information: str,
                               doctor_id: int, have_medicine: bool,
                               medicine_orders: List[dict] = None) -> bool:
        """
        完整的患者就诊流程

        Args:
            registration_id: 挂号ID
            information: 病历内容
            doctor_id: 医生ID
            have_medicine: 是否开药
            medicine_orders: 药品订单列表（如果需要开药）

        Returns:
            bool: 整个流程是否成功
        """
        try:
            # 1. 创建就诊记录
            record_success = self.create_patient_medical_record(registration_id, information, doctor_id, have_medicine)
            if not record_success:
                print("创建就诊记录失败")
                return False

            # 2. 如果开药，则执行开药操作
            if have_medicine and medicine_orders:
                prescribe_success = self.prescribe_medicines(registration_id, medicine_orders)
                if not prescribe_success:
                    print("开药操作失败")
                    return False
                print("就诊完成，已开药")
            elif not have_medicine:
                print("就诊完成，未开药")
            else:
                print("就诊记录已创建，但缺少药品订单信息")
                return False

            return True

        except Exception as e:
            print(f"完成就诊流程失败: {e}")
            return False

    def get_patient_visit_workflow(self, doctor_id: int, date: str) -> dict:
        """
        获取医生工作日的完整工作流程数据

        Args:
            doctor_id: 医生ID
            date: 日期 (YYYY-MM-DD)

        Returns:
            dict: 包含挂号列表和药品列表的完整数据
        """
        return {
            "registrations": self.get_doctor_daily_schedule(doctor_id, date),
            "medicines": self.get_medicines_for_prescription()
        }