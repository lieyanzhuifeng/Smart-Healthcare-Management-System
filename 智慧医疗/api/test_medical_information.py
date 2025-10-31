# test_patient_medical_records.py
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
    print("\n=== 患者病历接口测试系统 ===")
    print("1. 登录获取Token")
    print("2. 获取完整病历记录")
    print("4. 获取处方详情")
    print("6. 获取健康概览")
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
    print("\n--- 患者登录 ---")
    username = input("请输入用户名: ").strip()
    password = input("请输入密码: ").strip()
    role = input("请输入角色 (patient): ").strip() or "patient"

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
                token_preview = TOKEN[:20] + "..." if TOKEN and len(TOKEN) > 20 else TOKEN
                print(f"✅ 登录成功，Token: {token_preview}")

                # 获取患者ID信息
                headers = get_headers()
                if headers:
                    profile_response = requests.get(f"{BASE_URL}/patient/profile", headers=headers, timeout=10)
                    if profile_response.status_code == 200:
                        profile_data = profile_response.json()
                        if profile_data.get('code') == 200:
                            patient_info = profile_data.get('data', {})
                            print(f"👤 当前患者: {patient_info.get('name')} (ID: {patient_info.get('patientID')})")
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


def safe_int_format(value, default=0):
    """安全格式化整数"""
    try:
        if isinstance(value, (int, float)):
            return int(value)
        elif isinstance(value, str):
            return int(value)
        else:
            return default
    except (ValueError, TypeError):
        return default


def safe_str_format(value, default="", max_length=30):
    """安全格式化字符串"""
    try:
        if value is None:
            return default
        result = str(value)
        if len(result) > max_length:
            return result[:max_length - 3] + "..."
        return result
    except:
        return default


def test_get_medical_records():
    """测试获取完整病历记录"""
    print("\n--- 获取完整病历记录 ---")
    headers = get_headers()
    if not headers:
        return

    try:
        response = requests.get(f"{BASE_URL}/patient/medical-records", headers=headers, timeout=10)
        data = response.json()

        if data.get('code') == 200:
            records = data.get('data', [])
            if records:
                print(f"✅ 找到 {len(records)} 条病历记录:")
                print("=" * 100)
                for i, record in enumerate(records, 1):
                    print(f"\n📋 第 {i} 条病历:")
                    print(f"   📍 病历ID: {record.get('registrationId')}")
                    print(f"   🕒 就诊时间: {safe_str_format(record.get('time'))}")
                    print(f"   📝 诊断信息: {safe_str_format(record.get('information'), '无诊断信息')}")
                    print(f"   💊 是否有药: {'是' if record.get('haveMedicine') else '否'}")

                    doctor_info = record.get('doctor')
                    if doctor_info:
                        print(f"   👨‍⚕️ 医生信息:")
                        print(f"      - 姓名: {safe_str_format(doctor_info.get('doctorName'))}")
                        print(f"      - 科室: {safe_str_format(doctor_info.get('officeName'))}")
                        print(f"      - 专业: {safe_str_format(doctor_info.get('expertiseName'))}")

                    prescription = record.get('prescription', [])
                    if prescription:
                        print(f"   💊 处方药品 ({len(prescription)} 种):")
                        total_price = 0
                        for med in prescription:
                            total_price += med.get('totalPrice', 0)
                            print(
                                f"      - {med.get('medicineName')} x{med.get('amount')} (总价: {med.get('totalPrice')}元)")
                        print(f"   💰 处方总价: {total_price}元")
                    else:
                        print("   📝 无处方信息")

                    print("-" * 80)
            else:
                print("ℹ️  暂无病历记录")
        else:
            print(f"❌ 获取病历记录失败: {data.get('message')}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")



def test_get_prescription_details():
    """测试获取处方详情"""
    print("\n--- 获取处方详情 ---")
    headers = get_headers()
    if not headers:
        return

    # 先获取病历记录，让用户选择
    test_get_medical_records()

    registration_id = input("\n请输入要查看处方详情的病历ID: ").strip()
    if not registration_id:
        print("❌ 病历ID不能为空")
        return

    try:
        response = requests.get(
            f"{BASE_URL}/patient/medical-records/{registration_id}/prescription",
            headers=headers,
            timeout=10
        )
        data = response.json()

        if data.get('code') == 200:
            prescription_data = data.get('data', {})
            medicines = prescription_data.get('medicines', [])

            if medicines:
                print(f"✅ 病历 {registration_id} 的处方详情:")
                print("=" * 80)
                print(f"💊 药品数量: {prescription_data.get('medicineCount')}")
                print(f"💰 处方总价: {prescription_data.get('totalPrice')}元")
                print("\n📋 药品清单:")
                for i, medicine in enumerate(medicines, 1):
                    print(f"\n{i}. {medicine.get('medicineName')}:")
                    print(f"   - 药品ID: {medicine.get('medicineId')}")
                    print(f"   - 单价: {medicine.get('unitPrice')}元")
                    print(f"   - 数量: {medicine.get('amount')}")
                    print(f"   - 小计: {medicine.get('totalPrice')}元")
                    print(f"   - 描述: {safe_str_format(medicine.get('description'), '无描述')}")
            else:
                print(f"ℹ️  病历 {registration_id} 无处方信息")
        else:
            print(f"❌ 获取处方详情失败: {data.get('message')}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")




def test_get_health_overview():
    """测试获取健康概览"""
    print("\n--- 获取健康概览 ---")
    headers = get_headers()
    if not headers:
        return

    try:
        response = requests.get(f"{BASE_URL}/patient/health-overview", headers=headers, timeout=10)
        data = response.json()

        if data.get('code') == 200:
            overview = data.get('data', {})
            statistics = overview.get('statistics', {})
            recent_info = overview.get('recentInfo', {})

            print("🏥 健康概览:")
            print("=" * 60)

            print("\n📊 统计信息:")
            print(f"   📋 总病历数: {statistics.get('medicalRecords')}")
            print(f"   📅 待就诊预约: {statistics.get('upcomingAppointments')}")
            print(f"   🎫 总挂号次数: {statistics.get('totalRegistrations')}")
            print(f"   📈 处方率: {statistics.get('prescriptionRate')}%")

            print("\n🕒 最近信息:")
            print(f"   👨‍⚕️ 最近医生: {safe_str_format(recent_info.get('lastDoctor'), '无记录')}")
            print(f"   🕐 最近就诊: {safe_str_format(recent_info.get('lastVisit'))}")
            print(f"   🔄 更新时间: {safe_str_format(overview.get('lastUpdate'))}")

        else:
            print(f"❌ 获取健康概览失败: {data.get('message')}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")


def main():
    """主函数"""
    print("患者病历接口测试系统")
    print("请确保服务器正在 http://localhost:5000 运行")

    while True:
        print_menu()
        choice = input("请选择操作 (0-7): ").strip()

        if choice == '0':
            print("感谢使用，再见！")
            break
        elif choice == '1':
            login()
        elif choice == '2':
            test_get_medical_records()
        elif choice == '4':
            test_get_prescription_details()
        elif choice == '6':
            test_get_health_overview()
        else:
            print("❌ 无效选择，请重新输入！")

        input("\n按回车键继续...")


if __name__ == "__main__":
    main()