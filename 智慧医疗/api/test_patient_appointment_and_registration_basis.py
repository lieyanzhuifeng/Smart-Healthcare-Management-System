# test_patient_api.py
import requests
import json

BASE_URL = "http://localhost:5000"


def test_api(endpoint, method="GET", data=None, headers=None):
    """通用API测试函数"""
    url = f"{BASE_URL}{endpoint}"

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=data)
        elif method.upper() == "POST":
            if headers is None:
                headers = {}
            headers['Content-Type'] = 'application/json'
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            print(f"不支持的HTTP方法: {method}")
            return None

        print(f"\n{'=' * 60}")
        print(f"测试接口: {method} {endpoint}")
        if data:
            print(f"请求数据: {json.dumps(data, ensure_ascii=False)}")
        print(f"状态码: {response.status_code}")

        try:
            result = response.json()
            print("返回数据:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except:
            print(f"响应内容: {response.text}")

        print(f"{'=' * 60}")

        return response.json() if response.text else None

    except Exception as e:
        print(f"请求失败: {e}")
        return None


def test_patient_apis():
    """测试患者端所有API"""

    print("🚀 开始测试患者端API...")

    # 1. 先登录获取token
    print("\n1. 患者登录")
    login_data = {
        "username": "1",
        "password": "123456",
        "role": "patient"
    }
    login_result = test_api("/auth/login", "POST", login_data)

    if not login_result or login_result.get("code") != 200:
        print("❌ 登录失败，无法继续测试")
        return

    token = login_result["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ 获取到token: {token[:20]}...")

    # # 2. 测试获取患者个人信息
    # print("\n2. 测试获取患者个人信息")
    # test_api("/patient/profile", "GET", headers=headers)
    #
    # # 3. 测试获取所有科室
    # print("\n3. 测试获取所有科室")
    # test_api("/patient/offices", "GET", headers=headers)
    #
    # # 4. 测试根据科室获取医生列表
    # print("\n4. 测试根据科室获取医生列表")
    # test_api("/patient/doctors/by-office/1", "GET", headers=headers)  # 外科
    #
    # # 5. 测试获取医生排班
    # print("\n5. 测试获取医生排班")
    # test_api("/patient/schedule/doctor?doctorId=1&date=2025-10-27", "GET", headers=headers)
    #
    # # 6. 测试获取科室排班
    # print("\n6. 测试获取科室排班")
    # test_api("/patient/schedule/office?officeId=1&date=2025-10-27", "GET", headers=headers)

    # # 7. 测试获取预约列表
    # print("\n7. 测试获取预约列表")
    # test_api("/patient/appointments", "GET", headers=headers)

    # # 8. 测试创建预约
    # print("\n8. 测试创建预约")
    # appointment_data = {
    #     "sectionId": 194  # 使用有剩余名额的排班
    # }
    # create_result = test_api("/patient/appointments", "POST", appointment_data, headers)
    #
    # # 9. 测试取消预约（如果有有效预约）
    # print("\n9. 测试取消预约")
    # # 先获取预约列表找到有效的预约ID
    # appointments_result = test_api("/patient/appointments", "GET", headers=headers)
    # if appointments_result and appointments_result.get("code") == 200:
    #     appointments = appointments_result["data"]["appointments"]
    #     active_appointments = [a for a in appointments if a.get("state") == 1]  # 有效预约
    #     if active_appointments:
    #         appointment_id = active_appointments[0]["appointmentID"]
    #         test_api(f"/patient/appointments/{appointment_id}", "DELETE", headers=headers)

    # 10. 测试检查挂号可用性
    print("\n10. 测试检查挂号可用性")
    test_api("/patient/registration/availability?officeId=1&datetime=2025-10-27 10:00:00", "GET", headers=headers)

    # # 11. 测试检查预约可用性
    # print("\n11. 测试检查预约可用性")
    # test_api("/patient/registration/appointment-availability/194", "GET", headers=headers)

    # # 12. 测试获取挂号历史
    # print("\n12. 测试获取挂号历史")
    # test_api("/patient/registration/history", "GET", headers=headers)

    # # 13. 测试获取健康提醒
    # print("\n13. 测试获取健康提醒")
    # test_api("/patient/reminders", "GET", headers=headers)
    #
    # # 14. 测试获取检查报告
    # print("\n14. 测试获取检查报告")
    # test_api("/patient/reports", "GET", headers=headers)
    #
    # # 15. 测试连接
    # print("\n15. 测试连接")
    # test_api("/patient/test/connection", "GET", headers=headers)


def quick_patient_test():
    """快速测试患者核心功能"""
    print("⚡ 快速测试患者核心API...")

    # 登录
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

    # 测试核心功能
    test_api("/patient/appointments", "GET", headers=headers)  # 预约列表
    test_api("/patient/offices", "GET", headers=headers)  # 科室列表
    test_api("/patient/reminders", "GET", headers=headers)  # 健康提醒


if __name__ == "__main__":
    # 运行完整测试
    test_patient_apis()

    # 或者运行快速测试
    # quick_patient_test()

    print("\n🎉 患者端API测试完成！")