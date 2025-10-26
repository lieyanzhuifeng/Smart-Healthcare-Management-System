import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repository.medicine import MedicineRepository, PharmacyRepository, OrderRepository
from model import Medicine, Pharmacy, OrderForMedicine


def test_medicine_repository():
    """测试药品Repository"""
    print("🧪 测试药品Repository...")

    try:
        repo = MedicineRepository()

        # 获取所有药品
        medicines = repo.get_all_medicines()
        print(f"✅ 获取到 {len(medicines)} 种药品")

        if medicines:
            # 测试根据ID获取
            medicine = repo.get_medicine_by_id(medicines[0].medicineID)
            print(f"✅ 根据ID获取药品: {medicine.name}")

            # 测试搜索
            search_results = repo.search_medicines_by_name(medicine.name[:2])
            print(f"✅ 搜索到 {len(search_results)} 种药品")

        print("🎉 药品Repository测试完成")

    except Exception as e:
        print(f"❌ 测试失败: {e}")


def test_pharmacy_repository():
    """测试药房Repository"""
    print("\n🏥 测试药房Repository...")

    try:
        repo = PharmacyRepository()

        # 获取所有库存
        stock_list = repo.get_all_stock_info()
        print(f"✅ 获取到 {len(stock_list)} 条库存记录")

        if stock_list:
            # 测试获取单个库存
            stock = repo.get_medicine_stock(stock_list[0].medicineID)
            print(f"✅ 获取药品库存: 药品ID {stock.medicineID}, 数量 {stock.number}")

            # 测试低库存预警
            low_stock = repo.get_low_stock_medicines(100)
            print(f"✅ 低库存药品: {len(low_stock)} 种")

        print("🎉 药房Repository测试完成")

    except Exception as e:
        print(f"❌ 测试失败: {e}")


def test_order_repository():
    """测试订单Repository"""
    print("\n📝 测试订单Repository...")

    try:
        repo = OrderRepository()

        # 测试获取订单（如果有数据的话）
        # 这里需要根据您的实际数据调整inf_id
        test_inf_id = 1
        orders = repo.get_orders_by_information(test_inf_id)
        print(f"✅ 获取到 {len(orders)} 个订单")

        if orders:
            order_details = repo.get_orders_with_medicine_info(test_inf_id)
            print(f"✅ 获取到 {len(order_details)} 个订单详情")

        print("🎉 订单Repository测试完成")

    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    test_medicine_repository()
    test_pharmacy_repository()
    test_order_repository()