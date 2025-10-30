# test_change_password.py
import requests
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tool_of_test import test_api


def test_change_password_for_all_roles():
    """为所有四类角色设置初始密码"""
    print("🚀 开始为所有角色设置初始密码...")

    roles_test_cases = [
        {"role": "patient", "user_id": "1", "name": "mao"},
        {"role": "doctor", "user_id": "1", "name": "医生1"},
        {"role": "pharmacy", "user_id": "1", "name": "药房人员1"},
        {"role": "admin", "user_id": "1", "name": "管理员1"}
    ]

    results = {}

    for test_case in roles_test_cases:
        print(f"\n🔄 为 {test_case['role']} 设置密码...")

        # 第一步：先用任意密码登录（因为现在没有密码）
        print(f"1. 使用任意密码登录 {test_case['role']}")
        login_data = {
            "username": test_case["user_id"],
            "password": "any_password",  # 任意密码都可以，因为现在没有密码
            "role": test_case["role"]
        }

        login_result = test_api("/auth/login", "POST", login_data)

        if login_result and login_result.get("code") == 200:
            token = login_result["data"]["token"]
            print(f"   ✅ 登录成功，获取到token")

            # 第二步：设置新密码
            print(f"2. 为 {test_case['role']} 设置新密码")
            headers = {"Authorization": f"Bearer {token}"}
            change_password_data = {
                "old_password": "any_old_password",  # 对于没有密码的用户，旧密码可以是任意值
                "new_password": f"{test_case['role']}_password_123"  # 新密码
            }

            change_result = test_api("/auth/change-password", "POST", change_password_data, headers=headers)

            if change_result and change_result.get("code") == 200:
                print(f"   ✅ 密码设置成功!")

                # 第三步：验证新密码可以登录
                print(f"3. 验证新密码登录")
                new_login_data = {
                    "username": test_case["user_id"],
                    "password": f"{test_case['role']}_password_123",  # 使用新密码
                    "role": test_case["role"]
                }

                new_login_result = test_api("/auth/login", "POST", new_login_data)

                if new_login_result and new_login_result.get("code") == 200:
                    print(f"   ✅ 新密码登录成功!")
                    results[test_case["role"]] = "成功"

                    # 第四步：验证旧任意密码不能登录
                    print(f"4. 验证旧任意密码不能登录")
                    old_login_data = {
                        "username": test_case["user_id"],
                        "password": "any_password",  # 之前的任意密码
                        "role": test_case["role"]
                    }

                    old_login_result = test_api("/auth/login", "POST", old_login_data)

                    if old_login_result and old_login_result.get("code") != 200:
                        print(f"   ✅ 旧任意密码登录失败（符合预期）")
                    else:
                        print(f"   ⚠️  旧任意密码仍然可以登录")

                else:
                    print(f"   ❌ 新密码登录失败: {new_login_result.get('message', '未知错误')}")
                    results[test_case["role"]] = "新密码登录失败"
            else:
                print(f"   ❌ 密码设置失败: {change_result.get('message', '未知错误')}")
                results[test_case["role"]] = "密码设置失败"
        else:
            print(f"   ❌ 初始登录失败: {login_result.get('message', '未知错误')}")
            results[test_case["role"]] = "初始登录失败"

    return results


def test_error_cases():
    """测试修改密码的错误情况"""
    print("\n❌ 测试修改密码的错误情况...")

    # 1. 测试无效token
    print("1. 测试无效token")
    headers = {"Authorization": "Bearer invalid_token_123"}
    change_data = {
        "old_password": "any_password",
        "new_password": "new_password"
    }
    result = test_api("/auth/change-password", "POST", change_data, headers=headers)
    if result and result.get("code") != 200:
        print(f"   ✅ 无效token被拒绝: {result.get('message')}")
    else:
        print("   ❌ 无效token应该被拒绝")

    # 2. 测试缺少token
    print("2. 测试缺少token")
    result = test_api("/auth/change-password", "POST", change_data)
    if result and result.get("code") != 200:
        print(f"   ✅ 缺少token被拒绝: {result.get('message')}")
    else:
        print("   ❌ 缺少token应该被拒绝")

    # 3. 测试缺少参数
    print("3. 测试缺少参数")
    # 先获取一个有效token
    login_data = {
        "username": "1",
        "password": "any_password",
        "role": "patient"
    }
    login_result = test_api("/auth/login", "POST", login_data)
    if login_result and login_result.get("code") == 200:
        token = login_result["data"]["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 缺少new_password
        missing_data = {"old_password": "any_password"}
        result = test_api("/auth/change-password", "POST", missing_data, headers=headers)
        if result and result.get("code") != 200:
            print(f"   ✅ 缺少参数被拒绝: {result.get('message', '参数错误')}")
        else:
            print("   ❌ 缺少参数应该被拒绝")


def main():
    """主函数"""
    print("=" * 60)
    print("🔐 密码修改功能测试")
    print("=" * 60)

    # 测试为所有角色设置密码
    results = test_change_password_for_all_roles()

    # 测试错误情况
    test_error_cases()

    # 输出测试总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)

    success_count = 0
    total_count = len(results)

    for role, result in results.items():
        status = "✅ 成功" if result == "成功" else "❌ 失败"
        print(f"   {role}: {status} - {result}")
        if result == "成功":
            success_count += 1

    print(f"\n🎯 总体结果: {success_count}/{total_count} 个角色测试通过")

    if success_count == total_count:
        print("🎉 所有测试通过！密码修改功能正常工作")
    else:
        print("⚠️  部分测试失败，请检查代码实现")

    print("=" * 60)


if __name__ == "__main__":
    main()