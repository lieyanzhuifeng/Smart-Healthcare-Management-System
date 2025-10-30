# test_account_management.py
import requests
import json
import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tool_of_test import test_api


def test_account_management():
    """测试账户管理功能"""
    print("🚀 开始测试账户管理功能...")

    # # # 先登录一个管理员账户来测试（假设管理员有权限）
    # # print("\n1. 先登录管理员账户")
    # # login_data = {
    # #     "username": "1",
    # #     "password": "any_password",  # 任意密码
    # #     "role": "admin"
    # # }
    # # login_result = test_api("/auth/login", "POST", login_data)
    # #
    # # if not login_result or login_result.get("code") != 200:
    # #     print("❌ 管理员登录失败，无法继续测试")
    # #     return
    # #
    # # token = login_result["data"]["token"]
    # # headers = {"Authorization": f"Bearer {token}"}
    # # print("✅ 管理员登录成功")
    #
    # # 2. 测试创建新患者账户
    # print("\n2. 测试创建新患者账户")
    # new_patient_data = {
    #     "role": "patient",
    #     "name": "测试患者",
    #     "age": 25,
    #     "password": "test_patient_password"
    # }
    # create_result = test_api("/auth/account/create", "POST", new_patient_data)
    #
    # if create_result and create_result.get("code") == 200:
    #     new_patient_id = create_result["data"]["user_id"]
    #     print(f"✅ 创建患者账户成功，用户ID: {new_patient_id}")
    #
    #     # 3. 测试获取账户信息
    #     print("\n3. 测试获取账户信息")
    #     # 先登录新创建的患者账户
    #     patient_login_data = {
    #         "username": str(new_patient_id),
    #         "password": "test_patient_password",
    #         "role": "patient"
    #     }
    #     patient_login_result = test_api("/auth/login", "POST", patient_login_data)
    #
    #     if patient_login_result and patient_login_result.get("code") == 200:
    #         patient_token = patient_login_result["data"]["token"]
    #         patient_headers = {"Authorization": f"Bearer {patient_token}"}
    #         print("✅ 新患者账户登录成功")
    #
    #         # 获取账户信息
    #         info_result = test_api("/auth/account/info", "GET", headers=patient_headers)
    #         if info_result and info_result.get("code") == 200:
    #             account_info = info_result["data"]
    #             print(f"✅ 获取账户信息成功:")
    #             print(f"   用户ID: {account_info.get('user_id')}")
    #             print(f"   姓名: {account_info.get('name')}")
    #             print(f"   年龄: {account_info.get('age')}")
    #             print(f"   角色: {account_info.get('role')}")
    #         else:
    #             print(f"❌ 获取账户信息失败: {info_result.get('message', '未知错误')}")
    #
    #         # 4. 测试更新账户信息
    #         print("\n4. 测试更新账户信息")
    #         update_data = {
    #             "name": "更新后的测试患者",
    #             "age": 26
    #         }
    #         update_result = test_api("/auth/account/update", "POST", update_data, headers=patient_headers)
    #
    #         if update_result and update_result.get("code") == 200:
    #             print("✅ 更新账户信息成功")
    #
    #             # 验证更新结果
    #             verify_info = test_api("/auth/account/info", "GET", headers=patient_headers)
    #             if verify_info and verify_info.get("code") == 200:
    #                 updated_info = verify_info["data"]
    #                 if (updated_info.get('name') == "更新后的测试患者" and
    #                         updated_info.get('age') == 26):
    #                     print("✅ 账户信息更新验证成功")
    #                 else:
    #                     print("❌ 账户信息更新验证失败")
    #             else:
    #                 print("❌ 无法验证更新结果")
    #         else:
    #             print(f"❌ 更新账户信息失败: {update_result.get('message', '未知错误')}")
    #
    #         # 5. 测试删除账户
    #         print("\n5. 测试删除账户")
    #         delete_result = test_api("/auth/account/delete", "POST", headers=patient_headers)
    #
    #         if delete_result and delete_result.get("code") == 200:
    #             print("✅ 删除账户成功")
    #
    #             # 验证账户已被删除
    #             verify_delete = test_api("/auth/login", "POST", patient_login_data)
    #             if verify_delete and verify_delete.get("code") != 200:
    #                 print("✅ 账户删除验证成功（无法再登录）")
    #             else:
    #                 print("❌ 账户删除验证失败（仍然可以登录）")
    #         else:
    #             print(f"❌ 删除账户失败: {delete_result.get('message', '未知错误')}")
    #
    #     else:
    #         print(f"❌ 新患者账户登录失败: {patient_login_result.get('message', '未知错误')}")
    # else:
    #     print(f"❌ 创建患者账户失败: {create_result.get('message', '未知错误')}")

    # 6. 测试创建其他角色账户
    print("\n6. 测试创建医生账户")
    new_doctor_data = {
        "role": "doctor",
        "name": "测试医生",
        "age": 35,
        "expertiseID": 1,
        "officeID": 1,
        "positionID": 1,
        "NumberOfPatients": 0,
        "password": "test_doctor_password"
    }
    doctor_create_result = test_api("/auth/account/create", "POST", new_doctor_data)

    if doctor_create_result and doctor_create_result.get("code") == 200:
        new_doctor_id = doctor_create_result["data"]["user_id"]
        print(f"✅ 创建医生账户成功，用户ID: {new_doctor_id}")

        # 测试医生登录
        doctor_login_data = {
            "username": str(new_doctor_id),
            "password": "test_doctor_password",
            "role": "doctor"
        }
        doctor_login_result = test_api("/auth/login", "POST", doctor_login_data)

        if doctor_login_result and doctor_login_result.get("code") == 200:
            print("✅ 医生账户登录成功")

            # 清理：删除测试医生账户
            doctor_token = doctor_login_result["data"]["token"]
            doctor_headers = {"Authorization": f"Bearer {doctor_token}"}
            test_api("/auth/account/delete", "POST", headers=doctor_headers)
            print("✅ 清理测试医生账户")
        else:
            print("❌ 医生账户登录失败")
    else:
        print(f"❌ 创建医生账户失败: {doctor_create_result.get('message', '未知错误')}")

    # # 7. 测试退出登录
    # print("\n7. 测试退出登录")
    # logout_result = test_api("/auth/logout", "POST", headers=headers)
    # if logout_result and logout_result.get("code") == 200:
    #     print("✅ 退出登录成功")
    # else:
    #     print(f"❌ 退出登录失败: {logout_result.get('message', '未知错误')}")




def main():
    """主函数"""
    print("=" * 60)
    print("👥 账户管理功能测试")
    print("=" * 60)

    # 测试正常功能
    test_account_management()

    print("\n" + "=" * 60)
    print("🎉 账户管理功能测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()