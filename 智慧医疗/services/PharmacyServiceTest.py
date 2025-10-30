# test_pharmacy_service.py
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.PharmacyService import PharmacyService


def print_menu():
    """打印主菜单"""
    print("\n=== 药房服务测试系统 ===")
    print("1. 查看所有药品及库存信息")
    print("2. 查看待配药处方（状态2）")
    print("3. 查看已配药处方（状态3）")
    print("4. 查看已取药处方（状态4）")
    print("5. 配药操作")
    print("6. 取药操作")
    print("7. 查看指定状态的处方")
    print("0. 退出")


def input_registration_id():
    """输入挂号ID"""
    try:
        return int(input("请输入挂号ID: "))
    except ValueError:
        print("请输入有效的数字！")
        return None


def input_state():
    """输入状态"""
    try:
        state = int(input("请输入状态 (2:已开处方, 3:药品已准备, 4:已取药): "))
        if state not in [2, 3, 4]:
            print("状态必须是2、3或4")
            return None
        return state
    except ValueError:
        print("请输入有效的数字！")
        return None


def test_get_all_medicines_with_stock(service):
    """测试获取所有药品及库存信息"""
    print("\n--- 所有药品及库存信息 ---")
    medicines = service.get_all_medicines_with_stock()

    if not medicines:
        print("没有找到药品信息")
        return

    print(f"共找到 {len(medicines)} 种药品:")
    print("-" * 80)
    for i, medicine in enumerate(medicines, 1):
        print(f"{i:2d}. 药品ID: {medicine['medicineID']:3d} | "
              f"名称: {medicine['name']:15s} | "
              f"价格: {medicine['price']:6.2f}元 | "
              f"库存: {medicine['stock_number']:3d} | "
              f"描述: {medicine.get('description', '')}")


def test_get_prescriptions_by_state_2(service):
    """测试获取状态2的处方"""
    print("\n--- 待配药处方（状态2：已开处方） ---")
    prescriptions = service.get_prescriptions_by_state(2)

    if not prescriptions:
        print("没有待配药的处方")
        return

    print(f"共找到 {len(prescriptions)} 个待配药处方:")
    print("-" * 100)
    for i, prescription in enumerate(prescriptions, 1):
        print(f"{i:2d}. 处方ID: {prescription['registrationID']:4d} | "
              f"患者: {prescription['patient_name']:8s}({prescription['patient_age']:2d}岁) | "
              f"医生: {prescription.get('doctor_name', '未知'):8s} | "
              f"药品: {prescription.get('medicine_list', '无')} | "
              f"总价: {prescription.get('total_price', 0):6.2f}元")


def test_get_prescriptions_by_state_3(service):
    """测试获取状态3的处方"""
    print("\n--- 已配药处方（状态3：药品已准备） ---")
    prescriptions = service.get_prescriptions_by_state(3)

    if not prescriptions:
        print("没有已配药的处方")
        return

    print(f"共找到 {len(prescriptions)} 个已配药处方:")
    print("-" * 100)
    for i, prescription in enumerate(prescriptions, 1):
        print(f"{i:2d}. 处方ID: {prescription['registrationID']:4d} | "
              f"患者: {prescription['patient_name']:8s}({prescription['patient_age']:2d}岁) | "
              f"医生: {prescription.get('doctor_name', '未知'):8s} | "
              f"药品: {prescription.get('medicine_list', '无')} | "
              f"总价: {prescription.get('total_price', 0):6.2f}元")


def test_get_prescriptions_by_state_4(service):
    """测试获取状态4的处方"""
    print("\n--- 已取药处方（状态4：已取药） ---")
    prescriptions = service.get_prescriptions_by_state(4)

    if not prescriptions:
        print("没有已取药的处方")
        return

    print(f"共找到 {len(prescriptions)} 个已取药处方:")
    print("-" * 100)
    for i, prescription in enumerate(prescriptions, 1):
        print(f"{i:2d}. 处方ID: {prescription['registrationID']:4d} | "
              f"患者: {prescription['patient_name']:8s}({prescription['patient_age']:2d}岁) | "
              f"医生: {prescription.get('doctor_name', '未知'):8s} | "
              f"药品: {prescription.get('medicine_list', '无')} | "
              f"总价: {prescription.get('total_price', 0):6.2f}元")


def test_dispense_medicine(service):
    """测试配药操作"""
    print("\n--- 配药操作 ---")

    # 先显示待配药的处方
    pending_prescriptions = service.get_prescriptions_by_state(2)
    if not pending_prescriptions:
        print("没有待配药的处方")
        return

    print("待配药处方列表:")
    for i, prescription in enumerate(pending_prescriptions, 1):
        print(f"{i}. 处方ID: {prescription['registrationID']}, "
              f"患者: {prescription['patient_name']}, "
              f"药品: {prescription.get('medicine_list', '无')}")

    registration_id = input_registration_id()
    if not registration_id:
        return

    print(f"正在为处方 {registration_id} 配药...")
    result = service.dispense_medicine(registration_id)

    print("\n配药结果:")
    if result['success']:
        print("✅ 配药成功！")
        print(f"   处方ID: {result['registration_id']}")
        print(f"   药品清单: {result['medicine_list']}")
        print(f"   总价: {result['total_price']}元")
        if 'dispensed_medicines' in result:
            print("   详细清单:")
            for med in result['dispensed_medicines']:
                print(f"     - {med['medicine_name']} x{med['amount']} (单价:{med['price'] / med['amount']:.2f}元)")
    else:
        print("❌ 配药失败！")
        print(f"   错误信息: {result['message']}")
        if 'insufficient_medicines' in result:
            print("   缺货药品:")
            for med in result['insufficient_medicines']:
                print(f"     - {med['medicine_name']}: 需要{med['required']}，库存{med['current']}")


def test_take_medicine(service):
    """测试取药操作"""
    print("\n--- 取药操作 ---")

    # 先显示已配药的处方
    ready_prescriptions = service.get_prescriptions_by_state(3)
    if not ready_prescriptions:
        print("没有已配药的处方")
        return

    print("已配药处方列表:")
    for i, prescription in enumerate(ready_prescriptions, 1):
        print(f"{i}. 处方ID: {prescription['registrationID']}, "
              f"患者: {prescription['patient_name']}, "
              f"药品: {prescription.get('medicine_list', '无')}")

    registration_id = input_registration_id()
    if not registration_id:
        return

    print(f"正在为处方 {registration_id} 执行取药操作...")
    result = service.take_medicine(registration_id)

    print("\n取药结果:")
    if result['success']:
        print("✅ 取药成功！")
        print(f"   处方ID: {result['registration_id']}")
        if result['medicine_list']:
            print(f"   药品清单: {result['medicine_list']}")
            print(f"   总价: {result['total_price']}元")
        else:
            print("   （无药品信息）")
    else:
        print("❌ 取药失败！")
        print(f"   错误信息: {result['message']}")


def test_get_prescriptions_by_custom_state(service):
    """测试获取指定状态的处方"""
    print("\n--- 查看指定状态的处方 ---")

    state = input_state()
    if not state:
        return

    state_names = {2: "已开处方", 3: "药品已准备", 4: "已取药"}
    state_name = state_names.get(state, "未知状态")

    print(f"\n--- {state_name}的处方（状态{state}） ---")
    prescriptions = service.get_prescriptions_by_state(state)

    if not prescriptions:
        print(f"没有状态为{state}的处方")
        return

    print(f"共找到 {len(prescriptions)} 个处方:")
    print("-" * 100)
    for i, prescription in enumerate(prescriptions, 1):
        print(f"{i:2d}. 处方ID: {prescription['registrationID']:4d} | "
              f"患者: {prescription['patient_name']:8s}({prescription['patient_age']:2d}岁) | "
              f"医生: {prescription.get('doctor_name', '未知'):8s} | "
              f"药品: {prescription.get('medicine_list', '无')} | "
              f"总价: {prescription.get('total_price', 0):6.2f}元")


def main():
    """主函数"""
    try:
        print("正在初始化药房服务...")
        service = PharmacyService()
        print("药房服务初始化成功！")

        while True:
            print_menu()
            choice = input("请选择操作 (0-7): ").strip()

            if choice == '0':
                print("感谢使用，再见！")
                break
            elif choice == '1':
                test_get_all_medicines_with_stock(service)
            elif choice == '2':
                test_get_prescriptions_by_state_2(service)
            elif choice == '3':
                test_get_prescriptions_by_state_3(service)
            elif choice == '4':
                test_get_prescriptions_by_state_4(service)
            elif choice == '5':
                test_dispense_medicine(service)
            elif choice == '6':
                test_take_medicine(service)
            elif choice == '7':
                test_get_prescriptions_by_custom_state(service)
            else:
                print("无效选择，请重新输入！")

            input("\n按回车键继续...")

    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()