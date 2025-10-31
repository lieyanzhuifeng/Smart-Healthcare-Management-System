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
            print(f"  挂号ID: {reg['registrationID']},患者ID：{reg['patient_id']}, 患者: {reg['patient_name']}({reg['patient_age']}岁), "
                  f"状态: {reg['state']}, "
                  f"时间: {reg['date']} {reg['starttime']}-{reg['endtime']},"
                  f"序号：{reg['number']}")
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

    # 1. 查看医生某天的挂号列表
    print("\n步骤1: 查看医生排班")
    doctor_id, date = input_doctor_date()
    registrations = service.get_doctor_daily_schedule(doctor_id, date)

    if not registrations:
        print("该医生当天没有挂号记录")
        return False

    print(f"\n医生 {doctor_id} 在 {date} 的挂号列表:")
    for i, reg in enumerate(registrations, 1):
        print(f"  {i}. 挂号ID: {reg['registrationID']}, 患者ID：{reg['patient_id']},患者: {reg['patient_name']}({reg['patient_age']}岁), "
              f"状态: {reg['state']},时间: {reg['date']} {reg['starttime']}-{reg['endtime']}, 序号: {reg['number']}")

    # 2. 选择挂号开始问诊
    print("\n步骤2: 选择挂号开始问诊")
    try:
        choice = int(input("请选择要就诊的挂号编号 (输入前面的数字): "))
        if choice < 1 or choice > len(registrations):
            print("无效的选择")
            return False

        selected_reg = registrations[choice - 1]
        registration_id = selected_reg['registrationID']
        patient_name = selected_reg['patient_name']

        print(f"已选择患者: {patient_name}, 挂号ID: {registration_id}")

        # 开始就诊
        print(f"\n步骤3: 开始就诊")
        start_success = service.start_patient_visit(registration_id)
        if not start_success:
            print("开始就诊失败")
            return False
        print("就诊开始成功")

        # 3. 写病历
        print(f"\n步骤4: 填写病历")
        information = input("请输入病历内容: ")
        have_medicine = input("是否需要开药? (y/n): ").lower() == 'y'

        # 创建就诊记录
        record_success = service.create_patient_medical_record(
            registration_id, information, doctor_id, have_medicine
        )
        if not record_success:
            print("创建就诊记录失败")
            return False
        print("就诊记录创建成功")

        # 4. 如果需要开药，则开药
        if have_medicine:
            print(f"\n步骤5: 开药")
            # 显示所有药品
            medicines = service.get_medicines_for_prescription()
            print("\n可用药品列表:")
            for med in medicines:
                print(f"  药品ID: {med['medicineID']}, 名称: {med['name']}, 价格: {med['price']}元")

            medicine_orders = []
            while True:
                print("\n添加药品 (输入0结束):")
                try:
                    medicine_id = int(input("请输入药品ID: "))
                    if medicine_id == 0:
                        break
                    amount = int(input("请输入数量: "))
                    medicine_orders.append({"medicineID": medicine_id, "amount": amount})
                    print(f"已添加药品ID: {medicine_id}, 数量: {amount}")
                except ValueError:
                    print("请输入有效的数字！")

            if medicine_orders:
                prescribe_success = service.prescribe_medicines(registration_id, medicine_orders)
                if prescribe_success:
                    print("开药成功")
                else:
                    print("开药失败")
                    return False
            else:
                print("未添加任何药品")
        else:
            print("无需开药，就诊流程完成")

        print(f"\n✅ 完整就诊流程执行成功！")
        print(f"   患者: {patient_name}")
        print(f"   挂号ID: {registration_id}")
        print(f"   病历已记录: {information}")
        if have_medicine:
            print(f"   已开药: {len(medicine_orders)} 种药品")

        return True

    except ValueError:
        print("请输入有效的数字")
        return False
    except Exception as e:
        print(f"就诊流程执行失败: {e}")
        return False


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
            else:
                print("无效选择，请重新输入！")

            input("\n按回车键继续...")

    except Exception as e:
        print(f"程序运行出错: {e}")
        print("请检查数据库连接配置")


if __name__ == "__main__":
    main()