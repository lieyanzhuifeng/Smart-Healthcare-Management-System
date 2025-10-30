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

    def get_all_medicines_with_stock(self) -> List[Dict]:
        """
        获取所有药品信息及库存数量
        """
        query = """
            SELECT 
                m.medicineID,
                m.name,
                m.price,
                m.description,
                COALESCE(p.number, 0) as stock_number
            FROM medicine m
            LEFT JOIN pharmacy p ON m.medicineID = p.medicineID
            ORDER BY m.medicineID
        """
        try:
            results = self.execute_query(query)
            return results if results else []
        except Exception as e:
            print(f"获取药品及库存信息失败: {e}")
            return []

    def get_medicines_with_stock_by_name(self, name: str) -> List[Dict]:
        """
        根据药品名称搜索药品信息及库存数量
        """
        query = """
            SELECT 
                m.medicineID,
                m.name,
                m.price,
                m.description,
                COALESCE(p.number, 0) as stock_number
            FROM medicine m
            LEFT JOIN pharmacy p ON m.medicineID = p.medicineID
            WHERE m.name LIKE %s
            ORDER BY m.medicineID
        """
        try:
            results = self.execute_query(query, (f"%{name}%",))
            return results if results else []
        except Exception as e:
            print(f"搜索药品及库存信息失败: {e}")
            return []

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

    def dispense_medicine(self, registration_id: int) -> Dict:
        """
        为处方配药
        """
        try:
            # 1. 检查挂号状态是否为2（已开处方）
            registration_repo = RegistrationRepository()
            registration_info = registration_repo.get_registration_by_id(registration_id)

            if not registration_info:
                return {
                    'success': False,
                    'message': f'挂号记录 {registration_id} 不存在'
                }

            if registration_info['state'] != 2:
                return {
                    'success': False,
                    'message': f'挂号状态不允许配药，当前状态: {registration_info["state"]}，需要状态: 2'
                }

            # 2. 获取该处方的所有药品订单
            medical_order_repo = MedicalOrderRepository()
            orders_with_info = medical_order_repo.get_orders_with_medicine_info(registration_id)

            if not orders_with_info:
                return {
                    'success': False,
                    'message': f'处方 {registration_id} 没有药品订单'
                }

            # 3. 检查库存是否足够
            insufficient_stock_medicines = []
            for order in orders_with_info:
                medicine_id = order['medicineID']
                medicine_name = order['medicine_name']
                required_amount = order['amount']

                stock_info = self.get_medicine_stock(medicine_id)
                current_stock = stock_info.number if stock_info else 0

                if current_stock < required_amount:
                    insufficient_stock_medicines.append({
                        'medicine_id': medicine_id,
                        'medicine_name': medicine_name,
                        'required': required_amount,
                        'current': current_stock
                    })

            if insufficient_stock_medicines:
                medicine_list = ", ".join([
                    f"{med['medicine_name']}(需{med['required']}，库存{med['current']})"
                    for med in insufficient_stock_medicines
                ])
                return {
                    'success': False,
                    'message': f'库存不足，无法配药。缺货药品: {medicine_list}',
                    'insufficient_medicines': insufficient_stock_medicines
                }

            # 4. 减少库存
            for order in orders_with_info:
                medicine_id = order['medicineID']
                required_amount = order['amount']

                stock_success = self.decrease_stock(medicine_id, required_amount)
                if not stock_success:
                    return {
                        'success': False,
                        'message': f'减少药品ID {medicine_id} 库存失败'
                    }

            # 5. 更新挂号状态为3（药品已准备）
            update_success = registration_repo.update_registration_state(registration_id, 3)
            if not update_success:
                return {
                    'success': False,
                    'message': f'配药完成，但更新挂号状态失败'
                }

            # 6. 返回成功结果
            medicine_list = ", ".join([
                f"{order['medicine_name']} x{order['amount']}"
                for order in orders_with_info
            ])
            total_price = sum(order['price'] for order in orders_with_info)

            return {
                'success': True,
                'message': f'配药成功',
                'registration_id': registration_id,
                'medicine_list': medicine_list,
                'total_price': total_price,
                'dispensed_medicines': [
                    {
                        'medicine_id': order['medicineID'],
                        'medicine_name': order['medicine_name'],
                        'amount': order['amount'],
                        'price': order['price']
                    }
                    for order in orders_with_info
                ]
            }

        except Exception as e:
            print(f"配药操作失败: {e}")
            return {
                'success': False,
                'message': f'配药操作失败: {str(e)}'
            }

    def take_medicine(self, registration_id: int) -> Dict:
        """
        病人取药
        """
        try:
            # 1. 检查挂号状态是否为3（药品已准备）
            registration_repo = RegistrationRepository()
            registration_info = registration_repo.get_registration_by_id(registration_id)

            if not registration_info:
                return {
                    'success': False,
                    'message': f'挂号记录 {registration_id} 不存在'
                }

            if registration_info['state'] != 3:
                return {
                    'success': False,
                    'message': f'当前状态不允许取药，当前状态: {registration_info["state"]}，需要状态: 3（药品已准备）'
                }

            # 2. 获取药品订单信息（用于返回给用户）
            medical_order_repo = MedicalOrderRepository()
            orders_with_info = medical_order_repo.get_orders_with_medicine_info(registration_id)

            # 3. 更新挂号状态为4（已取药）
            update_success = registration_repo.update_registration_state(registration_id, 4)
            if not update_success:
                return {
                    'success': False,
                    'message': f'更新挂号状态失败'
                }

            # 4. 返回成功结果
            if orders_with_info:
                medicine_list = ", ".join([
                    f"{order['medicine_name']} x{order['amount']}"
                    for order in orders_with_info
                ])
                total_price = sum(order['price'] for order in orders_with_info)

                return {
                    'success': True,
                    'message': f'取药成功',
                    'registration_id': registration_id,
                    'medicine_list': medicine_list,
                    'total_price': total_price,
                    'patient_name': registration_info.get('patientsID', '未知患者'),
                    'medicines': [
                        {
                            'medicine_id': order['medicineID'],
                            'medicine_name': order['medicine_name'],
                            'amount': order['amount'],
                            'unit_price': order['unit_price'],
                            'total_price': order['price']
                        }
                        for order in orders_with_info
                    ]
                }
            else:
                return {
                    'success': True,
                    'message': f'取药成功（无药品信息）',
                    'registration_id': registration_id,
                    'medicine_list': '',
                    'total_price': 0,
                    'patient_name': registration_info.get('patientsID', '未知患者'),
                    'medicines': []
                }

        except Exception as e:
            print(f"取药操作失败: {e}")
            return {
                'success': False,
                'message': f'取药操作失败: {str(e)}'
            }


class MedicalOrderRepository(Base):
    """药品订单管理"""
    def __init__(self):
        super().__init__()
        self.registration_repo = RegistrationRepository()  # 在这里初始化

    def create_medicine_order(self, inf_id: int, medicine_id: int, amount: int, price: float) -> bool:
        """创建药品订单"""
        query = "INSERT INTO order_for_medicine (registrationID, medicineID, amount, price) VALUES (%s, %s, %s, %s)"
        result = self.execute_update(query, (inf_id, medicine_id, amount, price))
        return result > 0

    def get_orders_by_information(self, inf_id: int) -> List[OrderForMedicine]:
        """根据问诊信息获取订单"""
        query = "SELECT * FROM order_for_medicine WHERE registrationID = %s"
        results = self.execute_query(query, (inf_id,))
        return [OrderForMedicine.from_dict(row) for row in results] if results else []

    def get_orders_with_medicine_info(self, inf_id: int) -> List[Dict]:
        """根据问诊信息获取订单及药品详情"""
        query = """
                SELECT o.*, m.name as medicine_name, m.price as unit_price
                FROM order_for_medicine o
                         JOIN medicine m ON o.medicineID = m.medicineID
                WHERE o.registrationID = %s
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
                         JOIN information i ON o.registrationID = i.registrationID
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

    def get_prescriptions_by_state(self, state: int) -> List[Dict]:
        """
        根据状态获取处方信息和患者信息
        """
        query = """
            SELECT 
                r.registrationID,
                r.patientsID,
                p.name as patient_name,
                p.age as patient_age,
                r.sectionID,
                r.state,
                i.information,
                i.time as prescription_time,
                i.doctorID,
                d.name as doctor_name,
                GROUP_CONCAT(CONCAT(m.name, ' x', o.amount)) as medicine_list,
                SUM(o.price) as total_price
            FROM registration r
            JOIN patients p ON r.patientsID = p.patientsID
            LEFT JOIN information i ON r.registrationID = i.registrationID
            LEFT JOIN doctor d ON i.doctorID = d.doctorID
            LEFT JOIN order_for_medicine o ON r.registrationID = o.registrationID
            LEFT JOIN medicine m ON o.medicineID = m.medicineID
            WHERE r.state = %s
            GROUP BY r.registrationID
            ORDER BY i.time DESC
        """
        try:
            results = self.execute_query(query, (state,))
            return results if results else []
        except Exception as e:
            print(f"获取状态{state}的处方信息失败: {e}")
            return []