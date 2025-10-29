import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Optional, Dict
from model import Medicine, Pharmacy, OrderForMedicine, Registration
from repository.base import Base
from repository.registration import RegistrationRepository


class MedicineRepository(Base):
    """药品基本信息管理"""

    def get_all_medicines(self) -> List[Medicine]:
        """获取所有药品"""
        query = "SELECT * FROM medicine"
        results = self.execute_query(query)
        return [Medicine.from_dict(row) for row in results] if results else []

    def get_medicine_by_id(self, medicine_id: int) -> Optional[Medicine]:
        """根据ID获取药品"""
        query = "SELECT * FROM medicine WHERE medicineID = %s"
        result = self.execute_query(query, (medicine_id,))
        return Medicine.from_dict(result[0]) if result else None

    def search_medicines_by_name(self, name: str) -> List[Medicine]:
        """根据名称搜索药品"""
        query = "SELECT * FROM medicine WHERE name LIKE %s"
        results = self.execute_query(query, (f"%{name}%",))
        return [Medicine.from_dict(row) for row in results] if results else []

    def get_medicines_by_price_range(self, min_price: float, max_price: float) -> List[Medicine]:
        """根据价格范围获取药品"""
        query = "SELECT * FROM medicine WHERE price BETWEEN %s AND %s"
        results = self.execute_query(query, (min_price, max_price))
        return [Medicine.from_dict(row) for row in results] if results else []

    def create_medicine(self, name: str, price: float, description: str) -> bool:
        """创建新药品"""
        query = "INSERT INTO medicine (name, price, description) VALUES (%s, %s, %s)"
        result = self.execute_update(query, (name, price, description))
        return result > 0

    def update_medicine(self, medicine_id: int, name: str, price: float, description: str) -> bool:
        """更新药品信息"""
        query = "UPDATE medicine SET name = %s, price = %s, description = %s WHERE medicineID = %s"
        result = self.execute_update(query, (name, price, description, medicine_id))
        return result > 0


class PharmacyRepository(Base):
    """药品库存管理"""

    def get_medicine_stock(self, medicine_id: int) -> Optional[Pharmacy]:
        """获取药品库存"""
        query = "SELECT * FROM pharmacy WHERE medicineID = %s"
        result = self.execute_query(query, (medicine_id,))
        return Pharmacy.from_dict(result[0]) if result else None

    def update_medicine_stock(self, medicine_id: int, quantity: int) -> bool:
        """更新药品库存"""
        query = "UPDATE pharmacy SET number = %s WHERE medicineID = %s"
        result = self.execute_update(query, (quantity, medicine_id))
        return result > 0

    def get_all_stock_info(self) -> List[Pharmacy]:
        """获取所有库存信息"""
        query = "SELECT * FROM pharmacy"
        results = self.execute_query(query)
        return [Pharmacy.from_dict(row) for row in results] if results else []

    def get_low_stock_medicines(self, threshold: int = 10) -> List[Pharmacy]:
        """获取库存不足的药品"""
        query = "SELECT * FROM pharmacy WHERE number < %s"
        results = self.execute_query(query, (threshold,))
        return [Pharmacy.from_dict(row) for row in results] if results else []

    def increase_stock(self, medicine_id: int, quantity: int) -> bool:
        """增加药品库存"""
        current_stock = self.get_medicine_stock(medicine_id)
        if current_stock:
            new_quantity = current_stock.number + quantity
            return self.update_medicine_stock(medicine_id, new_quantity)
        return False

    def decrease_stock(self, medicine_id: int, quantity: int) -> bool:
        """减少药品库存"""
        current_stock = self.get_medicine_stock(medicine_id)
        if current_stock and current_stock.number >= quantity:
            new_quantity = current_stock.number - quantity
            return self.update_medicine_stock(medicine_id, new_quantity)
        return False


class MedicalOrderRepository(Base):
    """药品订单管理"""
    def __init__(self):
        super().__init__()
        self.registration_repo = RegistrationRepository()  # 在这里初始化

    def create_medicine_order(self, inf_id: int, medicine_id: int, amount: int, price: float) -> bool:
        """创建药品订单"""
        query = "INSERT INTO order_for_medicine (infID, medicineID, amount, price) VALUES (%s, %s, %s, %s)"
        result = self.execute_update(query, (inf_id, medicine_id, amount, price))
        return result > 0

    def get_orders_by_information(self, inf_id: int) -> List[OrderForMedicine]:
        """根据问诊信息获取订单"""
        query = "SELECT * FROM order_for_medicine WHERE infID = %s"
        results = self.execute_query(query, (inf_id,))
        return [OrderForMedicine.from_dict(row) for row in results] if results else []

    def get_orders_with_medicine_info(self, inf_id: int) -> List[Dict]:
        """根据问诊信息获取订单及药品详情"""
        query = """
                SELECT o.*, m.name as medicine_name, m.price as unit_price
                FROM order_for_medicine o
                         JOIN medicine m ON o.medicineID = m.medicineID
                WHERE o.infID = %s
                """
        return self.execute_query(query, (inf_id,))

    def get_order_by_id(self, order_id: int) -> Optional[OrderForMedicine]:
        """根据ID获取订单"""
        query = "SELECT * FROM order_for_medicine WHERE orderID = %s"
        result = self.execute_query(query, (order_id,))
        return OrderForMedicine.from_dict(result[0]) if result else None

    def delete_order(self, order_id: int) -> bool:
        """删除订单"""
        query = "DELETE FROM order_for_medicine WHERE orderID = %s"
        result = self.execute_update(query, (order_id,))
        return result > 0

    def get_orders_by_patient(self, patient_id: int) -> List[Dict]:
        """根据患者获取订单历史"""
        query = """
                SELECT o.*, m.name as medicine_name, i.time as order_time
                FROM order_for_medicine o
                         JOIN medicine m ON o.medicineID = m.medicineID
                         JOIN information i ON o.infID = i.infID
                WHERE i.patientIsD = %s
                ORDER BY i.time DESC
                """
        return self.execute_query(query, (patient_id,))

    # 为患者开药
    def prescribe_medicine(self, registration_id: int, medicine_orders: List[dict]) -> bool:
        try:
            # 验证挂号是否存在且状态正确（应该是就诊中状态）
            registration_info = self.registration_repo.get_registration_by_id(registration_id)
            if not registration_info:
                print(f"挂号记录 {registration_id} 不存在")
                return False

            # 检查挂号状态是否为就诊中（允许开药）
            if registration_info['state'] != Registration.STATE_IN_PROGRESS:
                print(f"挂号 {registration_id} 状态不允许开药，当前状态: {registration_info['state']}")
                return False

            # 遍历药品订单，插入订单记录
            for order in medicine_orders:
                medicine_id = order.get('medicineID')
                amount = order.get('amount')

                if not medicine_id or not amount:
                    print("药品订单数据不完整，跳过")
                    continue

                # 获取药品价格
                price_query = "SELECT price FROM medicine WHERE medicineID = %s"
                price_result = self.execute_query(price_query, (medicine_id,))

                if not price_result:
                    print(f"药品ID {medicine_id} 不存在，跳过")
                    continue

                medicine_price = price_result[0]['price']
                total_price = medicine_price * amount

                # 插入订单记录
                insert_query = """
                    INSERT INTO order_for_medicine (registrationID, medicineID, amount, price) 
                    VALUES (%s, %s, %s, %s)
                """
                result = self.execute_update(insert_query, (registration_id, medicine_id, amount, total_price))

                if result > 0:
                    print(f"药品订单插入成功: 药品ID {medicine_id}, 数量 {amount}, 总价 {total_price}")
                else:
                    print(f"药品订单插入失败: 药品ID {medicine_id}")
                    return False

            # 所有药品订单插入成功后，将挂号状态更新为已开处方
            update_success = self.registration_repo.update_registration_state(registration_id,
                                                                              Registration.STATE_PRESCRIBED)
            if update_success:
                print(f"开药完成，挂号 {registration_id} 状态已更新为已开处方")
            else:
                print(f"开药完成，但挂号 {registration_id} 状态更新失败")

            return update_success

        except Exception as e:
            print(f"开药操作失败: {e}")
            return False