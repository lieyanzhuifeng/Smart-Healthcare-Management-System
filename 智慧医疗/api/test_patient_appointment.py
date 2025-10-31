# test_simple_registration_flow.py
from tool_of_test import test_api


def test_simple_registration_flow():
    """简化版挂号流程测试 - 从选择科室到挂号"""
    print("🚀 简化版挂号流程测试")
    print("=" * 60)

    # 1. 患者登录
    print("\n1. 患者登录")
    login_data = {
        "username": "1",
        "password": "123456",
        "role": "patient"
    }
    login_result = test_api("/auth/login", "POST", login_data)

    if not login_result or login_result.get("code") != 200:
        print("❌ 登录失败")
        return

    token = login_result["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")

    # 2. 获取所有科室
    print("\n2. 获取所有科室")
    offices_result = test_api("/patient/offices", "GET", headers=headers)

    if not offices_result or offices_result.get("code") != 200:
        print("❌ 获取科室失败")
        return

    offices = offices_result["data"]
    print(f"✅ 获取到 {len(offices)} 个科室")
    for office in offices:
        print(f"  - {office['name']} (ID: {office['officeID']})")

    # 3. 选择第一个科室（外科）
    office_id = 1
    print(f"\n3. 选择科室: 外科 (ID: {office_id})")

    # 4. 获取该科室的医生列表
    print(f"\n4. 获取外科的医生列表")
    doctors_result = test_api(f"/patient/doctors/by-office/{office_id}", "GET", headers=headers)

    if not doctors_result or doctors_result.get("code") != 200:
        print("❌ 获取医生列表失败")
        return

    doctors = doctors_result["data"]
    print(f"✅ 获取到 {len(doctors)} 位医生")
    for doctor in doctors:
        print(f"  - {doctor['doctor_name']} (ID: {doctor['doctorID']}) - {doctor['position_name']}")

    # 5. 选择第一个医生
    doctor_id = 16
    print(f"\n5. 选择医生: 医生16 (ID: {doctor_id})")

    # 6. 获取医生排班（使用固定日期）
    print(f"\n6. 获取医生排班 - 日期: 2025-11-1")

    schedule_result = test_api(f"/patient/schedule/doctor?doctorId={doctor_id}&date=2025-11-1", "GET", headers=headers)

    if not schedule_result or schedule_result.get("code") != 200:
        print("❌ 获取排班失败")
        return

    schedules = schedule_result["data"]
    print(f"✅ 获取到 {len(schedules)} 个排班")
    for schedule in schedules:
        print(
            f"  - 排班ID: {schedule['sectionID']}, 时间: {schedule['starttime']}-{schedule['endtime']}, 剩余名额: {schedule['restappiontment']}")

    if not schedules:
        print("❌ 该医生没有排班，无法继续")
        return

    # 7. 选择第一个排班进行挂号
    section_id = schedules[0]['sectionID']
    print(f"\n7. 选择排班进行挂号 - 排班ID: {section_id}")

    # 先创建预约
    print("\n7.1 创建预约")
    appointment_data = {
        "sectionId": section_id
    }
    appointment_result = test_api("/patient/appointments", "POST", appointment_data, headers)

    if appointment_result and appointment_result.get("code") == 200:
        print("✅ 预约创建成功")


    # 8. 查看最终结果
    print("\n8.1 查看预约列表")
    test_api("/patient/appointments", "GET", headers=headers)


if __name__ == "__main__":
    # 运行完整测试
    test_simple_registration_flow()

    print("\n🎉 患者端API测试完成！")