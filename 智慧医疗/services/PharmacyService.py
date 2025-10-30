import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, Dict
from repository.medicine import MedicineRepository,PharmacyRepository,MedicalOrderRepository
from repository.registration import RegistrationRepository

class PharmacyService:
    """药房服务类，整合药品管理相关功能"""

    def __init__(self):
        self.medicine_repo = MedicineRepository()
        self.pharmacy_repo = PharmacyRepository()
        self.medical_order_repo = MedicalOrderRepository()
        self.registration_repo = RegistrationRepository()

    def get_all_medicines_with_stock(self) -> List[Dict]:
        """
        获取所有药品信息及库存数量

        Returns:
            List[Dict]: 包含药品信息和库存数量的字典列表
        """
        return self.medicine_repo.get_all_medicines_with_stock()


    def dispense_medicine(self, registration_id: int) -> Dict:
        """
        为处方配药

        Args:
            registration_id: 挂号ID

        Returns:
            Dict: 配药结果信息
        """
        return self.pharmacy_repo.dispense_medicine(registration_id)

    def take_medicine(self, registration_id: int) -> Dict:
        """
        病人取药

        Args:
            registration_id: 挂号ID

        Returns:
            Dict: 取药结果信息
        """
        return self.pharmacy_repo.take_medicine(registration_id)

    def get_prescriptions_by_state(self, state: int) -> List[Dict]:
        """
        根据状态获取处方信息和患者信息

        Args:
            state: 挂号状态 (2:已开处方, 3:药品已准备, 4:已取药)

        Returns:
            List[Dict]: 包含处方信息和患者信息的字典列表
        """
        return self.medical_order_repo.get_prescriptions_by_state(state)
