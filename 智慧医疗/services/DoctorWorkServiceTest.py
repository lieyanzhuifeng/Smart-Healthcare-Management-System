# test_doctor_workflow.py
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.DoctorWorkService import DoctorWorkService

def print_menu():
    """打印主菜单"""
    print("\n=== 医生工作流程测试系统 ===")
    print("1. 查看医生某天的挂号列表")
    print("2. 开始患者就诊")
    print("3. 创建就诊记录")
    print("4. 为患者开药")
    print("5. 查看所有药品信息")
    print("6. 完整就诊流程")
    print("7. 获取完整工作流程数据")
    print("0. 退出")


def input_doctor_date():
    """输入医生ID和日期"""
    doctor_id = int(input("请输入医生ID: "))
    date = input("请输入日期 (YYYY-MM-DD): ")
    return doctor_id, date


def input_registration_id():
    """输入挂号ID"""
    return int(input("请输入挂号ID: "))


def test_get_daily_schedule(service):
    """测试获取医生每日排班"""
    print("\n--- 获取医生每日排班 ---")
    doctor_id, date = input_doctor_date()

    registrations = service.get_doctor_daily_schedule(doctor_id, date)

    if registrations:
        print(f"\n医生 {doctor_id} 在 {date} 的有效挂号信息:")
        for reg in registrations:
            print(f"  挂号ID: {reg['registrationID']}, 患者: {reg['patient_name']}({reg['patient_age']}岁), "
                  f"状态: {service.registration_repo.get_registration_state_description(reg['state'])}, "
                  f"时间: {reg['date']} {reg['starttime']}-{reg['endtime']}")
    else:
        print("未找到相关挂号信息")


def test_start_visit(service):
    """测试开始就诊"""
    print("\n--- 开始患者就诊 ---")
    registration_id = input_registration_id()

    success = service.start_patient_visit(registration_id)
    if success:
        print(f"挂号 {registration_id} 已开始就诊")
    else:
        print(f"挂号 {registration_id} 开始就诊失败")


def test_create_medical_record(service):
    """测试创建就诊记录"""
    print("\n--- 创建就诊记录 ---")
    registration_id = input_registration_id()
    information = input("请输入病历内容: ")
    doctor_id = int(input("请输入医生ID: "))
    have_medicine = input("是否开药? (y/n): ").lower() == 'y'

    success = service.create_patient_medical_record(registration_id, information, doctor_id, have_medicine)
    if success:
        print("就诊记录创建成功")
    else:
        print("就诊记录创建失败")


def test_prescribe_medicines(service):
    """测试开药功能"""
    print("\n--- 为患者开药 ---")
    registration_id = input_registration_id()

    # 先显示所有药品
    medicines = service.get_medicines_for_prescription()
    print("\n可用药品列表:")
    for med in medicines:
        print(f"  药品ID: {med['medicineID']}, 名称: {med['name']}, 价格: {med['price']}元")

    medicine_orders = []
    while True:
        print("\n添加药品 (输入0结束):")
        medicine_id = int(input("请输入药品ID: "))
        if medicine_id == 0:
            break
        amount = int(input("请输入数量: "))
        medicine_orders.append({"medicineID": medicine_id, "amount": amount})
        print(f"已添加药品ID: {medicine_id}, 数量: {amount}")

    if medicine_orders:
        success = service.prescribe_medicines(registration_id, medicine_orders)
        if success:
            print("开药成功")
        else:
            print("开药失败")
    else:
        print("未添加任何药品")


def test_get_all_medicines(service):
    """测试获取所有药品信息"""
    print("\n--- 所有药品信息 ---")
    medicines = service.get_all_medicines()

    if medicines:
        for medicine in medicines:
            print(f"  药品ID: {medicine.medicineID}, 名称: {medicine.name}, "
                  f"价格: {medicine.price}元, 描述: {medicine.description}")
    else:
        print("未找到药品信息")


def test_complete_visit_workflow(service):
    """测试完整就诊流程"""
    print("\n--- 完整就诊流程 ---")
    registration_id = input_registration_id()
    information = input("请输入病历内容: ")
    doctor_id = int(input("请输入医生ID: "))
    have_medicine = input("是否开药? (y/n): ").lower() == 'y'

    medicine_orders = []
    if have_medicine:
        # 显示所有药品
        medicines = service.get_medicines_for_prescription()
        print("\n可用药品列表:")
        for med in medicines:
            print(f"  药品ID: {med['medicineID']}, 名称: {med['name']}, 价格: {med['price']}元")

        while True:
            print("\n添加药品 (输入0结束):")
            medicine_id = int(input("请输入药品ID: "))
            if medicine_id == 0:
                break
            amount = int(input("请输入数量: "))
            medicine_orders.append({"medicineID": medicine_id, "amount": amount})
            print(f"已添加药品ID: {medicine_id}, 数量: {amount}")

    success = service.complete_patient_visit(registration_id, information, doctor_id, have_medicine, medicine_orders)
    if success:
        print("完整就诊流程执行成功")
    else:
        print("完整就诊流程执行失败")


def test_get_workflow_data(service):
    """测试获取完整工作流程数据"""
    print("\n--- 获取完整工作流程数据 ---")
    doctor_id, date = input_doctor_date()

    workflow_data = service.get_patient_visit_workflow(doctor_id, date)

    print(f"\n医生 {doctor_id} 在 {date} 的工作数据:")

    print("\n挂号列表:")
    if workflow_data["registrations"]:
        for reg in workflow_data["registrations"]:
            print(f"  挂号ID: {reg['registrationID']}, 患者: {reg['patient_name']}({reg['patient_age']}岁)")
    else:
        print("  无挂号信息")

    print("\n药品列表:")
    if workflow_data["medicines"]:
        for med in workflow_data["medicines"]:
            print(f"  药品ID: {med['medicineID']}, 名称: {med['name']}, 价格: {med['price']}元")
    else:
        print("  无药品信息")


def main():
    """主函数"""
    try:
        print("正在初始化医生工作服务...")
        service = DoctorWorkService()
        print("服务初始化成功！")

        while True:
            print_menu()
            choice = input("请选择操作 (0-7): ").strip()

            if choice == '0':
                print("感谢使用，再见！")
                break
            elif choice == '1':
                test_get_daily_schedule(service)
            elif choice == '2':
                test_start_visit(service)
            elif choice == '3':
                test_create_medical_record(service)
            elif choice == '4':
                test_prescribe_medicines(service)
            elif choice == '5':
                test_get_all_medicines(service)
            elif choice == '6':
                test_complete_visit_workflow(service)
            elif choice == '7':
                test_get_workflow_data(service)
            else:
                print("无效选择，请重新输入！")

            input("\n按回车键继续...")

    except Exception as e:
        print(f"程序运行出错: {e}")
        print("请检查数据库连接配置")


if __name__ == "__main__":
    main()