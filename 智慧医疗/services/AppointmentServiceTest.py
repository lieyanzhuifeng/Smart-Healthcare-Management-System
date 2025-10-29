# test_appointment_service_fixed.py
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.AppointmentService import AppointmentService


def get_user_input(prompt, input_type=str):
    """获取用户输入"""
    try:
        user_input = input(prompt).strip()
        if input_type == int:
            return int(user_input) if user_input else None
        return user_input if user_input else None
    except ValueError:
        print("输入格式错误，请重新输入")
        return None
    except KeyboardInterrupt:
        print("\n用户取消输入")
        return None


def test_appointment_service_fixed():
    """修复后的 AppointmentService 测试 - 按业务逻辑流程"""
    print("=== 预约服务业务流程测试 ===")

    # 创建服务实例
    service = AppointmentService()

    while True:
        print("\n" + "=" * 50)
        print("预约服务主菜单")
        print("=" * 50)
        print("1. 开始新的预约流程")
        print("2. 退出测试")

        choice = get_user_input("请选择 (1-2): ", int)

        if choice == 2:
            print("退出预约服务测试")
            break
        elif choice != 1:
            print("无效选择，请重新输入")
            continue

        # 步骤1: 列出所有科室
        print("\n步骤1: 选择科室")
        print("-" * 30)
        offices = service.get_all_offices()

        if not offices:
            print("没有可用的科室")
            continue

        print(f"共有 {len(offices)} 个科室:")
        for i, office in enumerate(offices, 1):
            print(f"  {i}. {office.name} (ID: {office.officeID})")

        # 选择科室
        office_choice = get_user_input(f"\n请选择科室 (1-{len(offices)}): ", int)
        if not office_choice or office_choice < 1 or office_choice > len(offices):
            print("无效的科室选择")
            continue

        selected_office = offices[office_choice - 1]
        test_office_id = selected_office.officeID
        test_office_name = selected_office.name

        print(f"\n✅ 已选择科室: {test_office_name}")

        # 步骤2: 选择搜索方式
        while True:
            print("\n步骤2: 选择搜索方式")
            print("-" * 30)
            print("1. 按医生搜索 - 先选择医生，再选择日期")
            print("2. 按日期搜索 - 搜索该科室在某日期的所有排班")
            print("3. 返回科室选择")

            search_choice = get_user_input("请选择搜索方式 (1-3): ", int)

            if search_choice == 1:
                search_by_doctor(service, test_office_id, test_office_name)
            elif search_choice == 2:
                search_by_date(service, test_office_id, test_office_name)
            elif search_choice == 3:
                break
            else:
                print("无效选择，请重新输入")


def search_by_doctor(service, office_id, office_name):
    """按医生搜索排班"""
    print(f"\n--- 按医生搜索 - {office_name} ---")

    # 获取该科室的医生列表
    doctors = service.get_doctors_by_office(office_id)

    if not doctors:
        print(f"{office_name} 科室下没有医生")
        return

    print(f"\n{office_name} 科室的医生列表:")
    for i, doctor in enumerate(doctors, 1):
        print(f"  {i}. {doctor.doctor_name} - {doctor.position_name}")
        print(f"     年龄：{doctor.age}")
        print(f"     专长: {doctor.expertise_name}, 已接诊患者: {doctor.NumberOfPatients}人")
        print(f"     医生ID: {doctor.doctorID}")
        print()

    # 选择医生
    doctor_choice = get_user_input(f"请选择医生 (1-{len(doctors)}): ", int)
    if not doctor_choice or doctor_choice < 1 or doctor_choice > len(doctors):
        print("无效的医生选择")
        return

    selected_doctor = doctors[doctor_choice - 1]
    test_doctor_id = selected_doctor.doctorID
    doctor_name = selected_doctor.doctor_name

    print(f"\n✅ 已选择医生: {doctor_name}")

    # 输入日期
    test_date = get_user_input("请输入要查询的日期 (格式: YYYY-MM-DD): ")
    if not test_date:
        print("日期不能为空")
        return

    # 获取医生排班信息
    print(f"\n正在查询 {doctor_name} 在 {test_date} 的排班信息...")
    doctor_schedule = service.get_doctor_schedule_by_date(test_doctor_id, test_date)

    if not doctor_schedule:
        print(f"医生 {doctor_name} 在 {test_date} 没有排班")
        return

    print(f"\n📅 {doctor_name} 在 {test_date} 的排班信息:")
    for i, schedule in enumerate(doctor_schedule, 1):
        rest_appointments = schedule.get('restappiontment', 0)
        status = "🟢 可预约" if rest_appointments > 0 else "🔴 已满"

        print(f"  {i}. 排班ID: {schedule.get('sectionID')}")
        print(f"     时间: {schedule.get('starttime')} - {schedule.get('endtime')}")
        print(f"     剩余名额: {rest_appointments} {status}")
        print()

    # 询问是否创建预约
    create_appointment_choice = get_user_input("是否要为此医生创建预约? (y/n): ")
    if create_appointment_choice and create_appointment_choice.lower() == 'y':
        patients_id = get_user_input("请输入患者ID: ", int)
        if patients_id:
            section_choice = get_user_input("请选择排班编号: ", int)
            if section_choice and 1 <= section_choice <= len(doctor_schedule):
                selected_section = doctor_schedule[section_choice - 1]
                section_id = selected_section.get('sectionID')

                print(f"\n正在为患者 {patients_id} 创建预约...")
                result = service.create_appointment(patients_id, section_id)

                print("\n创建预约结果:")
                print(f"  成功: {result.get('success')}")
                print(f"  消息: {result.get('message')}")
                if result.get('appointment_id'):
                    print(f"  预约ID: {result.get('appointment_id')}")


def search_by_date(service, office_id, office_name):
    """按日期搜索排班"""
    print(f"\n--- 按日期搜索 - {office_name} ---")

    # 输入日期
    test_date = get_user_input("请输入要查询的日期 (格式: YYYY-MM-DD): ")
    if not test_date:
        print("日期不能为空")
        return

    # 获取科室排班信息
    print(f"\n正在查询 {office_name} 在 {test_date} 的所有排班...")
    office_schedule = service.get_office_schedule_by_date(office_id, test_date)

    if not office_schedule:
        print(f"{office_name} 在 {test_date} 没有排班")
        return

    print(f"\n📅 {office_name} 在 {test_date} 的排班信息:")

    # 按医生分组显示
    doctors_schedule = {}
    for schedule in office_schedule:
        doctor_id = schedule.doctorID
        if doctor_id not in doctors_schedule:
            doctors_schedule[doctor_id] = {
                'doctor_name': schedule.doctor_name,
                'position': schedule.position_name,
                'expertise': schedule.expertise_name,
                'age': schedule.age,
                'schedules': []
            }
        doctors_schedule[doctor_id]['schedules'].append(schedule)

    for i, (doctor_id, doctor_info) in enumerate(doctors_schedule.items(), 1):
        print(f"\n  {i}. 医生: {doctor_info['doctor_name']}")
        print(f"     年龄：{doctor_info['age']}")
        print(f"     职位: {doctor_info['position']}, 专长: {doctor_info['expertise']}")
        print(f"     排班详情:")

        for j, schedule in enumerate(doctor_info['schedules'], 1):
            rest_appointments = schedule.restappiontment
            status = "🟢 可预约" if rest_appointments > 0 else "🔴 已满"

            print(f"       {j}. 排班ID: {schedule.sectionID}")
            print(f"           时间: {schedule.starttime} - {schedule.endtime}")
            print(f"           剩余名额: {rest_appointments} {status}")

    # 询问是否创建预约
    create_appointment_choice = get_user_input("\n是否要创建预约? (y/n): ")
    if create_appointment_choice and create_appointment_choice.lower() == 'y':
        patients_id = get_user_input("请输入患者ID: ", int)
        if patients_id:
            # 让用户选择具体的排班
            all_schedules = []
            for doctor_info in doctors_schedule.values():
                all_schedules.extend(doctor_info['schedules'])

            print(f"\n请选择排班 (1-{len(all_schedules)}):")
            for k, schedule in enumerate(all_schedules, 1):
                print(
                    f"  {k}. {schedule.doctor_name} - {schedule.starttime}~{schedule.endtime} (排班ID: {schedule.sectionID})")

            section_choice = get_user_input("请输入排班编号: ", int)
            if section_choice and 1 <= section_choice <= len(all_schedules):
                selected_section = all_schedules[section_choice - 1]
                section_id = selected_section.sectionID

                print(f"\n正在为患者 {patients_id} 创建 {selected_section.doctor_name} 医生的预约...")
                result = service.create_appointment(patients_id, section_id)

                print("\n创建预约结果:")
                print(f"  成功: {result.get('success')}")
                print(f"  消息: {result.get('message')}")
                if result.get('appointment_id'):
                    print(f"  预约ID: {result.get('appointment_id')}")


def test_appointment_operations():
    """测试预约操作功能"""
    print("\n" + "=" * 50)
    print("开始测试预约操作功能")
    print("=" * 50)

    service = AppointmentService()

    while True:
        print("\n请选择要测试的功能:")
        print("1. 创建预约")
        print("2. 取消预约")
        print("3. 获取患者预约信息")
        print("4. 返回主菜单")

        choice = get_user_input("请输入选择 (1-4): ", int)

        if choice == 1:
            test_create_appointment(service)
        elif choice == 2:
            test_cancel_appointment(service)
        elif choice == 3:
            test_get_patient_appointments(service)
        elif choice == 4:
            break
        else:
            print("无效选择，请重新输入")


def test_create_appointment(service):
    """测试创建预约"""
    print("\n--- 测试创建预约 ---")

    patients_id = get_user_input("请输入患者ID: ", int)
    if not patients_id:
        print("患者ID不能为空")
        return

    section_id = get_user_input("请输入排班ID: ", int)
    if not section_id:
        print("排班ID不能为空")
        return

    print(f"\n正在为患者 {patients_id} 创建排班 {section_id} 的预约...")
    result = service.create_appointment(patients_id, section_id)

    print("\n创建预约结果:")
    print(f"  成功: {result.get('success')}")
    print(f"  消息: {result.get('message')}")
    if result.get('section_id'):
        print(f"  排班ID: {result.get('section_id')}")


def test_cancel_appointment(service):
    """测试取消预约"""
    print("\n--- 测试取消预约 ---")

    appointment_id = get_user_input("请输入预约ID: ", int)
    if not appointment_id:
        print("预约ID不能为空")
        return

    print(f"\n正在取消预约ID {appointment_id}...")
    result = service.cancel_appointment(appointment_id)

    print("\n取消预约结果:")
    print(f"  成功: {result.get('success')}")
    print(f"  消息: {result.get('message')}")
    if result.get('appointment_id'):
        print(f"  预约ID: {result.get('appointment_id')}")


def test_get_patient_appointments(service):
    """测试获取患者预约信息"""
    print("\n--- 测试获取患者预约信息 ---")

    patients_id = get_user_input("请输入患者ID: ", int)
    if not patients_id:
        print("患者ID不能为空")
        return

    print(f"\n正在获取患者 {patients_id} 的预约信息...")
    result = service.get_patient_appointments(patients_id)

    print("\n获取预约信息结果:")
    print(f"  成功: {result.get('success')}")

    if result.get('success'):
        stats = result.get('statistics', {})
        print(f"  统计信息:")
        print(f"    总预约数: {stats.get('total', 0)}")
        print(f"    有效预约: {stats.get('active', 0)}")
        print(f"    已取消: {stats.get('cancelled', 0)}")
        print(f"    已完成: {stats.get('completed', 0)}")

        appointments = result.get('appointments', [])
        print(f"\n  预约详情 ({len(appointments)} 条):")
        for i, appointment in enumerate(appointments[:10], 1):  # 只显示前10条
            print(f"    {i}. 预约ID: {appointment.get('appointmentID')}")
            print(f"       排班ID: {appointment.get('sectionID')}")
            print(f"       医生: {appointment.get('doctor_name')}")
            print(f"       科室: {appointment.get('office_name')}")
            print(f"       专长: {appointment.get('expertise_name')}")
            print(f"       职位: {appointment.get('position_name')}")
            print(f"       日期: {appointment.get('date')}")
            print(f"       时间: {appointment.get('starttime')} - {appointment.get('endtime')}")
            print(f"       状态: {appointment.get('state')}")
            print()

        if len(appointments) > 10:
            print(f"    ... 还有 {len(appointments) - 10} 条记录")
    else:
        print(f"  错误消息: {result.get('message')}")




def main():
    """主测试函数"""
    try:
        print("=== 预约服务综合测试 ===")

        while True:
            print("\n请选择测试模式:")
            print("1. 基础功能测试 (科室、医生、排班查询)")
            print("2. 预约操作测试 (创建、取消、查询预约)")
            print("3. 退出测试")

            choice = get_user_input("请输入选择 (1-4): ", int)

            if choice == 1:
                test_appointment_service_fixed()
            elif choice == 2:
                test_appointment_operations()
            elif choice == 3:
                print("感谢使用测试程序！")
                break
            else:
                print("无效选择，请重新输入")

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
    print("\n所有测试完成！")