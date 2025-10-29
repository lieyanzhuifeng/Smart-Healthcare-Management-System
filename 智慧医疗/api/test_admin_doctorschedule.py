# test_admin_schedule.py
import requests
import json

from tool_of_test import test_api

def test_admin_schedule_workflow():
    """测试管理员排班完整流程"""
    print("🚀 开始测试管理员排班功能...")

    # 1. 先登录获取管理员token
    print("\n1. 管理员登录获取token")
    login_data = {
        "username": "1",  # 管理员ID 1
        "password": "123456",
        "role": "admin"
    }
    login_result = test_api("/auth/login", "POST", login_data)

    if not login_result or login_result.get("code") != 200:
        print("❌ 管理员登录失败，无法继续测试")
        return

    admin_token = login_result["data"]["token"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    print(f"✅ 获取到管理员token: {admin_token[:30]}...")

    # # 2. 测试健康检查
    # print("\n2. 测试管理员健康检查")
    # test_api("/admin/health", "GET", headers=headers)

    # # 3. 生成排班（预览）
    # print("\n3. 生成排班预览")
    # generate_data = {
    #     "startDate": "2025-10-29",
    #     "endDate": "2025-10-29",
    #     "timeslots": [3]  # 只生成上午和下午的排班
    # }
    # generate_result = test_api("/admin/schedules/generate", "POST", generate_data, headers)
    #
    # if not generate_result or generate_result.get("code") != 200:
    #     print("❌ 生成排班失败")
    #     return
    #
    # schedules = generate_result["data"]["schedules"]
    # print(f"✅ 成功生成 {len(schedules)} 条排班记录")
    #
    # # 4. 保存排班到数据库
    # if schedules:
    #     print("\n4. 保存排班到数据库")
    #     save_data = {
    #         "schedules": schedules
    #     }
    #     save_result = test_api("/admin/schedules/save", "POST", save_data, headers)

    # 5. 测试一键生成并保存
    print("\n5. 测试一键生成并保存")
    quick_generate_data = {
        "startDate": "2025-10-29",
        "endDate": "2025-10-29",
        "timeslots": [4]  # 只生成上午排班
    }
    test_api("/admin/schedules/generate-and-save", "POST", quick_generate_data, headers)

    # 6. 测试预览排班
    print("\n6. 测试预览排班")
    test_api("/admin/schedules/preview?date=2025-10-29", "GET", headers=headers)

    # # 7. 测试清除排班
    # print("\n7. 测试清除排班")
    # clear_data = {
    #     "startDate": "2025-10-29",
    #     "endDate": "2025-10-29"
    # }
    # test_api("/admin/schedules/clear", "POST", clear_data, headers)

    # # 8. 测试其他管理功能
    # print("\n8. 测试管理统计数据")
    # test_api("/admin/statistics", "GET", headers=headers)
    #
    # print("\n9. 测试门诊量趋势")
    # test_api("/admin/statistics/outpatient-trend?days=7", "GET", headers=headers)
    #
    # print("\n10. 测试科室分布")
    # test_api("/admin/statistics/department-distribution", "GET", headers=headers)


def test_admin_without_permission():
    """测试无权限访问"""
    print("\n🔒 测试无权限访问（用患者token访问管理员接口）")

    # 先用患者登录
    patient_login_data = {
        "username": "1",
        "password": "123456",
        "role": "patient"
    }
    patient_login = test_api("/auth/login", "POST", patient_login_data)

    if patient_login and patient_login.get("code") == 200:
        patient_token = patient_login["data"]["token"]
        headers = {"Authorization": f"Bearer {patient_token}"}

        # 用患者token尝试访问管理员接口
        print("\n用患者token尝试生成排班（应该失败）")
        generate_data = {
            "startDate": "2025-01-20",
            "endDate": "2025-01-21"
        }
        test_api("/admin/schedules/generate", "POST", generate_data, headers)


if __name__ == "__main__":
    # 测试完整的排班流程
    test_admin_schedule_workflow()

    # 测试权限控制
    #test_admin_without_permission()

    print("\n🎉 管理员排班功能测试完成！")