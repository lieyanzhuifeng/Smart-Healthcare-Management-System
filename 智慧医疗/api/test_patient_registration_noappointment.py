# test_register_patient_direct.py
from tool_of_test import test_api


def test_register_patient_direct():
    """直接测试挂号功能"""
    print("🚀 直接测试挂号功能")
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

    # 2. 测试直接挂号（无预约）
    print("\n2. 测试直接挂号（无预约患者）")
    registration_data = {
        "officeId": 1,  # 外科
        "datetime": "2025-10-29 23:10:00"  # 未来时间
    }

    result = test_api("/patient/registration/register", "POST", registration_data, headers)

    if result and result.get("code") == 200:
        print("✅ 直接挂号成功！")
        print(f"挂号详情: {result.get('data')}")
    else:
        print("❌ 直接挂号失败")
        if result:
            print(f"失败原因: {result.get('message')}")


    # 3. 查看最终的挂号历史
    print("\n4. 查看挂号历史")
    test_api("/patient/registration/history", "GET", headers=headers)


if __name__ == "__main__":
    test_register_patient_direct()
    print("\n🎉 挂号功能测试完成！")