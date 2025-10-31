# test_doctor_manual.py
import requests
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:5000"
TOKEN = None


def print_menu():
    """打印测试菜单"""
    print("\n=== 医生接口集成测试系统 ===")
    print("1. 登录获取Token")
    print("2. 查看今日患者")
    print("3. 开始患者就诊")
    print("4. 创建就诊记录")
    print("5. 查看药品列表")
    print("6. 创建电子处方")
    print("7. 获取AI诊断建议")
    print("8. 完整就诊流程测试")
    print("0. 退出")


def get_headers():
    """获取带认证的请求头"""
    if not TOKEN:
        print("❌ 请先登录获取Token")
        return None
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }


def login():
    """手动输入登录信息"""
    global TOKEN
    print("\n--- 用户登录 ---")
    username = input("请输入用户名: ").strip()
    password = input("请输入密码: ").strip()
    role = input("请输入角色 (doctor): ").strip() or "doctor"

    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "username": username,
            "password": password,
            "role": role
        }, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                TOKEN = data.get('data', {}).get('token')
                print(f"✅ 登录成功，Token: {TOKEN[:20]}...")
            else:
                print(f"❌ 登录失败: {data.get('message')}")
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("❌ 连接失败，请确保服务器正在运行")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 发生错误: {e}")


def test_get_today_patients():
    """测试获取今日患者"""
    print("\n--- 获取今日患者 ---")
    headers = get_headers()
    if not headers:
        return

    try:
        response = requests.get(f"{BASE_URL}/doctor/patients/today", headers=headers, timeout=10)
        data = response.json()

        if data.get('code') == 200:
            patients = data.get('data', [])
            if patients:
                print(f"✅ 找到 {len(patients)} 个患者:")
                for i, patient in enumerate(patients, 1):
                    print(f"  {i}. {patient['patientName']}({patient['patientAge']}岁) - "
                          f"状态: {patient['status']} - 挂号ID: {patient['registrationId']} - "
                          f"时间段：{patient['appointmentTime']} - 第{patient['queueNumber']}位")
            else:
                print("ℹ️  今日没有患者")
        else:
            print(f"❌ 获取失败: {data.get('message')}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")


def test_start_visit():
    """测试开始就诊"""
    print("\n--- 开始患者就诊 ---")
    headers = get_headers()
    if not headers:
        return

    registration_id = input("请输入挂号ID: ").strip()
    if not registration_id:
        print("❌ 挂号ID不能为空")
        return

    try:
        response = requests.post(
            f"{BASE_URL}/doctor/patients/{registration_id}/start-visit",
            headers=headers,
            json={},
            timeout=10
        )
        data = response.json()

        if data.get('code') == 200:
            print("✅ 就诊开始成功")
        else:
            print(f"❌ 开始就诊失败: {data.get('message')}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")


def test_create_medical_record():
    """测试创建就诊记录"""
    print("\n--- 创建就诊记录 ---")
    headers = get_headers()
    if not headers:
        return

    registration_id = input("请输入挂号ID: ").strip()
    if not registration_id:
        print("❌ 挂号ID不能为空")
        return

    information = input("请输入病历内容: ").strip()
    if not information:
        print("❌ 病历内容不能为空")
        return

    have_medicine = input("是否开药? (y/n): ").strip().lower() == 'y'

    try:
        response = requests.post(
            f"{BASE_URL}/doctor/patients/{registration_id}/medical-record",
            headers=headers,
            json={
                "information": information,
                "haveMedicine": have_medicine
            },
            timeout=10
        )
        data = response.json()

        if data.get('code') == 200:
            print("✅ 就诊记录创建成功")
        else:
            print(f"❌ 创建就诊记录失败: {data.get('message')}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")


def test_get_medicines():
    """测试获取药品列表"""
    print("\n--- 获取药品列表 ---")
    headers = get_headers()
    if not headers:
        return

    try:
        response = requests.get(f"{BASE_URL}/doctor/medicines", headers=headers, timeout=10)
        data = response.json()

        if data.get('code') == 200:
            medicines = data.get('data', [])
            if medicines:
                print(f"✅ 找到 {len(medicines)} 种药品:")
                for i, medicine in enumerate(medicines, 1):
                    print(f"  {i}. {medicine['name']} - ID: {medicine['medicineID']} - "
                          f"价格: {medicine['price']}元")
            else:
                print("ℹ️  没有药品数据")
        else:
            print(f"❌ 获取药品失败: {data.get('message')}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")


def test_create_prescription():
    """测试创建电子处方"""
    print("\n--- 创建电子处方 ---")
    headers = get_headers()
    if not headers:
        return

    registration_id = input("请输入挂号ID: ").strip()
    if not registration_id:
        print("❌ 挂号ID不能为空")
        return

    # 先显示药品列表
    test_get_medicines()

    medicines = []
    while True:
        print("\n添加药品 (输入0结束):")
        medicine_id = input("请输入药品ID: ").strip()
        if medicine_id == '0':
            break
        amount = input("请输入数量: ").strip()

        if medicine_id and amount:
            try:
                medicines.append({
                    "medicineID": int(medicine_id),
                    "amount": int(amount)
                })
                print(f"✅ 已添加药品ID: {medicine_id}, 数量: {amount}")
            except ValueError:
                print("❌ 请输入有效的数字")
        else:
            print("❌ 药品ID和数量不能为空")

    if not medicines:
        print("❌ 未添加任何药品")
        return

    try:
        response = requests.post(
            f"{BASE_URL}/doctor/prescriptions",
            headers=headers,
            json={
                "registrationId": int(registration_id),
                "medicines": medicines
            },
            timeout=10
        )
        data = response.json()

        if data.get('code') == 200:
            print("✅ 处方创建成功")
        else:
            print(f"❌ 处方创建失败: {data.get('message')}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")


def test_ai_diagnose():
    """测试AI诊断建议"""
    print("\n--- 获取AI诊断建议 ---")
    headers = get_headers()
    if not headers:
        return

    patient_id = input("请输入患者ID: ").strip()
    if not patient_id:
        print("❌ 患者ID不能为空")
        return

    try:
        response = requests.get(
            f"{BASE_URL}/doctor/ai-diagnose/{patient_id}",
            headers=headers,
            timeout=10
        )
        data = response.json()

        if data.get('code') == 200:
            ai_data = data.get('data', {})
            print("✅ AI诊断建议:")
            print(f"  可能诊断: {ai_data.get('possibleDiagnosis')}")
            print(f"  建议检查: {ai_data.get('suggestedTests')}")
            print(f"  用药建议: {ai_data.get('medicationSuggestions')}")
            print(f"  注意事项: {ai_data.get('notes')}")
        else:
            print(f"❌ 获取AI诊断失败: {data.get('message')}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")


def test_complete_workflow():
    """完整就诊流程测试"""
    print("\n--- 完整就诊流程测试 ---")
    headers = get_headers()
    if not headers:
        return

    # 1. 查看今日患者
    print("\n步骤1: 查看今日患者")
    test_get_today_patients()

    # 2. 选择挂号开始就诊
    print("\n步骤2: 开始就诊")
    registration_id = input("请输入要就诊的挂号ID: ").strip()
    if not registration_id:
        print("❌ 挂号ID不能为空")
        return

    # 开始就诊
    try:
        response = requests.post(
            f"{BASE_URL}/doctor/patients/{registration_id}/start-visit",
            headers=headers,
            json={},
            timeout=10
        )
        start_data = response.json()

        if start_data.get('code') == 200:
            print("✅ 就诊开始成功")
        else:
            print(f"❌ 开始就诊失败: {start_data.get('message')}")
            return
    except Exception as e:
        print(f"❌ 开始就诊错误: {e}")
        return

    # 3. 创建就诊记录
    print("\n步骤3: 创建就诊记录")
    information = input("请输入病历内容: ").strip()
    if not information:
        print("❌ 病历内容不能为空")
        return

    have_medicine = input("是否开药? (y/n): ").strip().lower() == 'y'

    try:
        response = requests.post(
            f"{BASE_URL}/doctor/patients/{registration_id}/medical-record",
            headers=headers,
            json={
                "information": information,
                "haveMedicine": have_medicine
            },
            timeout=10
        )
        record_data = response.json()

        if record_data.get('code') == 200:
            print("✅ 就诊记录创建成功")
        else:
            print(f"❌ 创建就诊记录失败: {record_data.get('message')}")
            return
    except Exception as e:
        print(f"❌ 创建就诊记录错误: {e}")
        return

    # 4. 如果需要开药
    if have_medicine:
        print("\n步骤4: 开具处方")
        test_create_prescription()

    print("\n🎉 完整就诊流程执行完成!")


def main():
    """主函数"""
    print("医生接口集成测试系统")
    print("请确保服务器正在 http://localhost:5000 运行")

    while True:
        print_menu()
        choice = input("请选择操作 (0-8): ").strip()

        if choice == '0':
            print("感谢使用，再见！")
            break
        elif choice == '1':
            login()
        elif choice == '2':
            test_get_today_patients()
        elif choice == '3':
            test_start_visit()
        elif choice == '4':
            test_create_medical_record()
        elif choice == '5':
            test_get_medicines()
        elif choice == '6':
            test_create_prescription()
        elif choice == '7':
            test_ai_diagnose()
        elif choice == '8':
            test_complete_workflow()
        else:
            print("❌ 无效选择，请重新输入！")

        input("\n按回车键继续...")


if __name__ == "__main__":
    main()