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
    """修复后的 AppointmentService 测试"""
    print("=== 开始修复后的 AppointmentService 测试 ===")

    # 创建服务实例
    service = AppointmentService()

    # 测试1: 获取所有科室
    print("\n1. 测试获取所有科室:")
    offices = service.get_all_offices()
    print(f"获取到 {len(offices)} 个科室")
    for i, office in enumerate(offices, 1):
        print(f"  {i}. 科室ID: {office.officeID}, 名称: {office.name}")

    # 手动输入测试参数
    print("\n" + "=" * 50)
    print("请手动输入测试参数")
    print("=" * 50)

    # 获取科室ID
    test_office_id = get_user_input("请输入要测试的科室ID: ", int)
    if not test_office_id:
        print("未输入科室ID，使用第一个科室")
        if offices:
            test_office_id = offices[0].officeID
            test_office_name = offices[0].name
        else:
            print("没有科室数据，无法继续测试")
            return
    else:
        # 验证科室是否存在
        office_exists = any(office.officeID == test_office_id for office in offices)
        if not office_exists:
            print(f"科室ID {test_office_id} 不存在，使用第一个科室")
            test_office_id = offices[0].officeID
        test_office_name = next((office.name for office in offices if office.officeID == test_office_id), "未知科室")

    print(f"\n使用科室测试 - ID: {test_office_id}, 名称: {test_office_name}")

    # 测试2: 获取科室下的医生
    print("\n2. 测试获取科室医生列表:")
    doctors = service.get_doctors_by_office(test_office_id)
    print(f"科室 {test_office_name} 下有 {len(doctors)} 个医生")
    for i, doctor in enumerate(doctors, 1):
        print(f"  {i}. 医生ID: {doctor.doctorID}, 姓名: {doctor.doctor_name}, "
              f"科室: {doctor.office_name}, 专长: {doctor.expertise_name}, 职位: {doctor.position_name}")

    # 获取医生ID
    test_doctor_id = None
    if doctors:
        test_doctor_id = get_user_input("请输入要测试的医生ID (直接回车使用第一个医生): ", int)
        if not test_doctor_id:
            test_doctor_id = doctors[0].doctorID
            print(f"使用医生ID: {test_doctor_id}")
    else:
        print("该科室没有医生，跳过医生相关测试")

    # 获取测试日期
    test_date = get_user_input("请输入测试日期 (格式: YYYY-MM-DD, 直接回车使用今天): ")
    if not test_date:
        test_date = datetime.now().strftime('%Y-%m-%d')
        print(f"使用日期: {test_date}")

    # 测试3: 获取医生排班信息
    if test_doctor_id:
        print(f"\n3. 测试获取医生排班信息 - 日期: {test_date}:")
        doctor_schedule = service.get_doctor_schedule_by_date(test_doctor_id, test_date)
        print(f"医生 {test_doctor_id} 在 {test_date} 有 {len(doctor_schedule)} 个排班")
        for i, schedule in enumerate(doctor_schedule, 1):
            print(f"  {i}. 排班ID: {schedule.get('sectionID')}, "
                  f"时间: {schedule.get('starttime')} - {schedule.get('endtime')}, "
                  f"剩余名额: {schedule.get('restappiontment')}")

    # 测试4: 获取科室排班信息
    print(f"\n4. 测试获取科室排班信息 - 日期: {test_date}:")
    office_schedule = service.get_office_schedule_by_date(test_office_id, test_date)
    print(f"科室 {test_office_name} 在 {test_date} 有 {len(office_schedule)} 条排班记录")
    for i, schedule in enumerate(office_schedule[:5], 1):  # 只显示前5条
        print(f"  {i}. 医生: {schedule.doctor_name}(ID:{schedule.doctorID}), "
              f"科室: {schedule.office_name}, 专长: {schedule.expertise_name}, 职位: {schedule.position_name}, "
              f"时间: {schedule.starttime} - {schedule.endtime}, "
              f"剩余名额: {schedule.restappiontment}")

    print("\n=== 基础功能测试完成 ===")


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


def test_appointment_availability(service):
    """测试预约可用性检查"""
    print("\n--- 测试预约可用性检查 ---")

    section_id = get_user_input("请输入排班ID: ", int)
    if not section_id:
        print("排班ID不能为空")
        return

    print(f"\n正在检查排班 {section_id} 的预约可用性...")
    result = service.check_appointment_availability(section_id)

    print("\n可用性检查结果:")
    print(f"  成功: {result.get('success')}")
    if result.get('success'):
        print(f"  排班ID: {result.get('section_id')}")
        print(f"  剩余名额: {result.get('restappiontment')}")
        print(f"  预约转挂号人数: {result.get('appiontmentconvert')}")
        print(f"  是否可用: {'是' if result.get('is_available') else '否'}")
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
            print("3. 预约可用性检查")
            print("4. 退出测试")

            choice = get_user_input("请输入选择 (1-4): ", int)

            if choice == 1:
                test_appointment_service_fixed()
            elif choice == 2:
                test_appointment_operations()
            elif choice == 3:
                service = AppointmentService()
                test_appointment_availability(service)
            elif choice == 4:
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