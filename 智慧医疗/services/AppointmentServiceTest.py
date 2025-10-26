# test_appointment_service_fixed.py
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.AppointmentService import AppointmentService


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

    # 如果有科室数据，继续测试其他功能
    if offices:
        # 使用第一个科室进行测试
        test_office_id = offices[0].officeID
        test_office_name = offices[0].name
        print(f"\n使用科室测试 - ID: {test_office_id}, 名称: {test_office_name}")

        # 测试2: 获取科室下的医生（修复后的视图格式）
        print("\n2. 测试获取科室医生列表（修复后的视图格式）:")
        doctors = service.get_doctors_by_office(test_office_id)
        print(f"科室 {test_office_name} 下有 {len(doctors)} 个医生")
        for i, doctor in enumerate(doctors[:3], 1):  # 只显示前3个
            print(f"  {i}. 医生ID: {doctor.doctorID}, 姓名: {doctor.doctor_name}, "
                  f"科室: {doctor.office_name}, 职位: {doctor.position_name}")

        # 如果有医生数据，继续测试排班功能
        if doctors:
            test_doctor_id = doctors[0].doctorID
            print(f"\n使用医生ID {test_doctor_id} 进行排班测试")

            # 测试3: 获取医生排班信息
            today = datetime.now().strftime('%Y-%m-%d')
            print(f"\n3. 测试获取医生排班信息 - 日期: {today}:")
            doctor_schedule = service.get_doctor_schedule_by_date(test_doctor_id, today)
            print(f"医生 {test_doctor_id} 在 {today} 有 {len(doctor_schedule)} 个排班")
            for i, schedule in enumerate(doctor_schedule, 1):
                print(f"  {i}. 排班ID: {schedule.get('sectionID')}, "
                      f"时间: {schedule.get('starttime')} - {schedule.get('endtime')}, "
                      f"剩余名额: {schedule.get('restappiontment')}")

            # 测试4: 获取科室排班信息（修复后的视图格式）
            print(f"\n4. 测试获取科室排班信息（修复后的视图格式） - 日期: {today}:")
            office_schedule = service.get_office_schedule_by_date(test_office_id, today)
            print(f"科室 {test_office_name} 在 {today} 有 {len(office_schedule)} 条排班记录")
            for i, schedule in enumerate(office_schedule[:3], 1):  # 只显示前3条
                print(f"  {i}. 医生: {schedule.doctor_name}(ID:{schedule.doctorID}), "
                      f"科室: {schedule.office_name}, 专业: {schedule.expertise_name}, "
                      f"时间: {schedule.starttime} - {schedule.endtime}, "
                      f"剩余名额: {schedule.restappiontment}")

        else:
            print(f"\n科室 {test_office_name} 没有医生数据，跳过排班测试")

        # 测试5: 直接测试排班查询（不依赖医生列表）
        print(f"\n5. 直接测试科室排班查询 - 日期: {today}:")
        office_schedule = service.get_office_schedule_by_date(test_office_id, today)
        print(f"直接查询结果: {len(office_schedule)} 条排班记录")

    else:
        print("\n警告: 没有获取到科室数据，无法进行完整测试")

    print("\n=== 修复后的 AppointmentService 测试完成 ===")


def test_basic_functionality():
    """测试基础功能"""
    print("\n=== 开始基础功能测试 ===")

    service = AppointmentService()

    # 测试基础数据获取
    offices = service.get_all_offices()
    print(f"科室数量: {len(offices)}")

    # 测试每个科室的医生和排班
    today = datetime.now().strftime('%Y-%m-%d')

    for office in offices:
        print(f"\n--- 测试科室: {office.name} ---")

        # 测试医生获取
        doctors = service.get_doctors_by_office(office.officeID)
        print(f"医生数量: {len(doctors)}")

        # 测试排班获取
        schedule = service.get_office_schedule_by_date(office.officeID, today)
        print(f"今日排班: {len(schedule)} 条")

        # 显示部分医生信息
        if doctors:
            for doctor in doctors[:2]:  # 只显示前2个
                print(f"  - {doctor.doctor_name} ({doctor.position_name})")

        # 显示部分排班信息
        if schedule:
            for s in schedule[:2]:  # 只显示前2个
                print(f"  - {s.doctor_name}: {s.starttime} - {s.endtime}")

    print("\n=== 基础功能测试完成 ===")


if __name__ == "__main__":
    try:
        test_appointment_service_fixed()
    except Exception as e:
        print(f"修复后的测试失败: {e}")
        import traceback

        traceback.print_exc()

    try:
        test_basic_functionality()
    except Exception as e:
        print(f"基础功能测试失败: {e}")
        import traceback

        traceback.print_exc()

    print("\n所有测试完成！")