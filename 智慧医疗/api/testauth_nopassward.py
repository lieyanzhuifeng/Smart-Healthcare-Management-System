import requests
import json
from tool_of_test import test_api


def test_all_roles_login():
    """测试所有四类角色的登录和基本信息"""
    print("🚀 开始测试所有四类角色登录和基本信息...")

    roles_test_cases = [
        {"role": "patient", "user_id": "1", "expected_name": "mao", "expected_age": 18},
        {"role": "doctor", "user_id": "1", "expected_name": "医生1", "expected_age": 20},
        {"role": "pharmacy", "user_id": "1", "expected_name": "药房人员1", "expected_age": 25},
        {"role": "admin", "user_id": "1", "expected_name": "管理员1", "expected_age": 35}
    ]

    tokens = {}

    for test_case in roles_test_cases:
        print(f"\n🔐 测试 {test_case['role']} 登录")
        login_data = {
            "username": test_case["user_id"],
            "password": "123456",  # 现在使用任意密码都可以，因为密码为NULL
            "role": test_case["role"]
        }
        login_result = test_api("/auth/login", "POST", login_data)

        if login_result and login_result.get("code") == 200:
            token = login_result["data"]["token"]
            tokens[test_case["role"]] = token
            print(f"✅ {test_case['role']} 登录成功!")
            print(f"📝 Token: {token[:30]}...")

            # 测试获取个人信息
            headers = {"Authorization": f"Bearer {token}"}
            profile_result = test_api("/auth/profile", "GET", headers=headers)

            if profile_result and profile_result.get("code") == 200:
                profile_data = profile_result["data"]
                print(f"✅ 获取到{test_case['role']}信息:")

                # 兼容不同的字段名
                user_id = profile_data.get('id') or profile_data.get('user_id')
                print(f"   ID: {user_id}")
                print(f"   姓名: {profile_data['name']}")
                print(f"   年龄: {profile_data['age']}")
                print(f"   角色: {profile_data['role']}")

                # 验证数据是否正确
                if (profile_data['name'] == test_case['expected_name'] and
                        profile_data['age'] == test_case['expected_age']):
                    print(f"✅ 数据验证正确!")
                else:
                    print(
                        f"❌ 数据验证失败! 期望: {test_case['expected_name']}({test_case['expected_age']}), 实际: {profile_data['name']}({profile_data['age']})")
            else:
                print(f"❌ 获取{test_case['role']}信息失败: {profile_result.get('message', '未知错误')}")
        else:
            print(f"❌ {test_case['role']}登录失败: {login_result.get('message', '未知错误')}")

    return tokens




if __name__ == "__main__":
    # 测试所有角色登录
    tokens = test_all_roles_login()
