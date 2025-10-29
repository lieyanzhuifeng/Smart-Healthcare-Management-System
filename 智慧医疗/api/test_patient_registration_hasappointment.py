# test_api_section_224.py
from tool_of_test import test_api


def test_api_section_224():
    """直接在API层测试section_id=224的预约转挂号"""
    print("🚀 直接在API层测试section_id=233")
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

    # 2. 直接测试section_id=224的预约转挂号
    print("\n2. 测试section_id=233的预约转挂号")
    registration_data = {
        "sectionId": 233
    }

    result = test_api("/patient/registration/register", "POST", registration_data, headers)

    if result and result.get("code") == 200:
        print("✅ API层预约转挂号成功！")
        print(f"挂号详情: {result.get('data')}")
    else:
        print("❌ API层预约转挂号失败")
        if result:
            print(f"失败原因: {result.get('message')}")

    # 3. 查看结果
    print("\n3. 查看结果")
    print("\n3.1 查看预约列表")
    test_api("/patient/appointments", "GET", headers=headers)

    print("\n3.2 查看挂号历史")
    test_api("/patient/registration/history", "GET", headers=headers)


if __name__ == "__main__":
    test_api_section_224()