# test_pharmacy_manual.py
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
    print("\n=== 药房接口集成测试系统 ===")
    print("1. 登录获取Token")
    print("2. 查看所有药品及库存")
    print("3. 查看待配药处方（状态2）")
    print("4. 查看已配药处方（状态3）")
    print("5. 查看已取药处方（状态4）")
    print("6. 按状态查询处方")
    print("7. 配药操作")
    print("8. 取药操作")
    print("10. 完整工作流程测试")
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
    print("\n--- 药房人员登录 ---")
    username = input("请输入用户名: ").strip()
    password = input("请输入密码: ").strip()
    role = input("请输入角色 (pharmacy): ").strip() or "pharmacy"

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


def safe_float_format(value, default=0.0):
    """安全格式化浮点数"""
    try:
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            return float(value)
        else:
            return default
    except (ValueError, TypeError):
        return default


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


def safe_str_format(value, default="", max_length=15):
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


def test_get_all_medicines():
    """测试获取所有药品及库存"""
    print("\n--- 获取所有药品及库存 ---")
    headers = get_headers()
    if not headers:
        return

    try:
        response = requests.get(f"{BASE_URL}/pharmacy/medicines", headers=headers, timeout=10)
        data = response.json()

        if data.get('code') == 200:
            medicines = data.get('data', [])
            if medicines:
                print(f"✅ 找到 {len(medicines)} 种药品:")
                print("-" * 80)
                for i, medicine in enumerate(medicines, 1):
                    medicine_id = safe_int_format(medicine.get('medicineID'), 0)
                    name = safe_str_format(medicine.get('name'), '未知药品')
                    price = safe_float_format(medicine.get('price'), 0.0)
                    stock = safe_int_format(medicine.get('stock_number'), 0)
                    description = safe_str_format(medicine.get('description'), '无描述', 20)

                    print(f"{i:2d}. 药品ID: {medicine_id:3d} | "
                          f"名称: {name:15s} | "
                          f"价格: {price:6.1f}元 | "
                          f"库存: {stock:3d} | "
                          f"描述: {description}")
            else:
                print("ℹ️  没有药品数据")
        else:
            print(f"❌ 获取药品失败: {data.get('message')}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")


def test_get_pending_prescriptions():
    """测试获取待配药处方"""
    print("\n--- 获取待配药处方（状态2） ---")
    headers = get_headers()
    if not headers:
        return

    try:
        response = requests.get(f"{BASE_URL}/pharmacy/prescriptions/pending", headers=headers, timeout=10)
        data = response.json()

        if data.get('code') == 200:
            prescriptions = data.get('data', [])
            if prescriptions:
                print(f"✅ 找到 {len(prescriptions)} 个待配药处方:")
                print("-" * 100)
                for i, prescription in enumerate(prescriptions, 1):
                    reg_id = safe_int_format(prescription.get('registrationID'), 0)
                    patient_name = safe_str_format(prescription.get('patient_name'), '未知患者', 8)
                    patient_age = safe_int_format(prescription.get('patient_age'), 0)
                    doctor_name = safe_str_format(prescription.get('doctor_name'), '未知医生', 8)
                    medicine_list = safe_str_format(prescription.get('medicine_list'), '无', 30)
                    total_price = safe_float_format(prescription.get('total_price'), 0.0)

                    print(f"{i:2d}. 处方ID: {reg_id:4d} | "
                          f"患者: {patient_name:8s}({patient_age:2d}岁) | "
                          f"医生: {doctor_name:8s} | "
                          f"药品: {medicine_list:30s} | "
                          f"总价: {total_price:6.1f}元")
            else:
                print("ℹ️  没有待配药处方")
        else:
            print(f"❌ 获取处方失败: {data.get('message')}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")


def test_get_ready_prescriptions():
    """测试获取已配药处方"""
    print("\n--- 获取已配药处方（状态3） ---")
    headers = get_headers()
    if not headers:
        return

    try:
        response = requests.get(f"{BASE_URL}/pharmacy/prescriptions/ready", headers=headers, timeout=10)
        data = response.json()

        if data.get('code') == 200:
            prescriptions = data.get('data', [])
            if prescriptions:
                print(f"✅ 找到 {len(prescriptions)} 个已配药处方:")
                print("-" * 100)
                for i, prescription in enumerate(prescriptions, 1):
                    reg_id = safe_int_format(prescription.get('registrationID'), 0)
                    patient_name = safe_str_format(prescription.get('patient_name'), '未知患者', 8)
                    patient_age = safe_int_format(prescription.get('patient_age'), 0)
                    doctor_name = safe_str_format(prescription.get('doctor_name'), '未知医生', 8)
                    medicine_list = safe_str_format(prescription.get('medicine_list'), '无', 30)
                    total_price = safe_float_format(prescription.get('total_price'), 0.0)

                    print(f"{i:2d}. 处方ID: {reg_id:4d} | "
                          f"患者: {patient_name:8s}({patient_age:2d}岁) | "
                          f"医生: {doctor_name:8s} | "
                          f"药品: {medicine_list:30s} | "
                          f"总价: {total_price:6.1f}元")
            else:
                print("ℹ️  没有已配药处方")
        else:
            print(f"❌ 获取处方失败: {data.get('message')}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")


def test_get_completed_prescriptions():
    """测试获取已取药处方"""
    print("\n--- 获取已取药处方（状态4） ---")
    headers = get_headers()
    if not headers:
        return

    try:
        response = requests.get(f"{BASE_URL}/pharmacy/prescriptions/completed", headers=headers, timeout=10)
        data = response.json()

        if data.get('code') == 200:
            prescriptions = data.get('data', [])
            if prescriptions:
                print(f"✅ 找到 {len(prescriptions)} 个已取药处方:")
                print("-" * 100)
                for i, prescription in enumerate(prescriptions, 1):
                    reg_id = safe_int_format(prescription.get('registrationID'), 0)
                    patient_name = safe_str_format(prescription.get('patient_name'), '未知患者', 8)
                    patient_age = safe_int_format(prescription.get('patient_age'), 0)
                    doctor_name = safe_str_format(prescription.get('doctor_name'), '未知医生', 8)
                    medicine_list = safe_str_format(prescription.get('medicine_list'), '无', 30)
                    total_price = safe_float_format(prescription.get('total_price'), 0.0)

                    print(f"{i:2d}. 处方ID: {reg_id:4d} | "
                          f"患者: {patient_name:8s}({patient_age:2d}岁) | "
                          f"医生: {doctor_name:8s} | "
                          f"药品: {medicine_list:30s} | "
                          f"总价: {total_price:6.1f}元")
            else:
                print("ℹ️  没有已取药处方")
        else:
            print(f"❌ 获取处方失败: {data.get('message')}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")


def test_get_prescriptions_by_state():
    """测试按状态查询处方"""
    print("\n--- 按状态查询处方 ---")
    headers = get_headers()
    if not headers:
        return

    state = input("请输入状态 (2:待配药, 3:已配药, 4:已取药): ").strip()
    if not state or state not in ['2', '3', '4']:
        print("❌ 状态必须是2、3或4")
        return

    try:
        response = requests.get(f"{BASE_URL}/pharmacy/prescriptions?state={state}", headers=headers, timeout=10)
        data = response.json()

        if data.get('code') == 200:
            result_data = data.get('data', {})
            prescriptions = result_data.get('prescriptions', [])
            status_name = result_data.get('status', '未知')

            if prescriptions:
                print(f"✅ 找到 {len(prescriptions)} 个{status_name}处方:")
                print("-" * 100)
                for i, prescription in enumerate(prescriptions, 1):
                    reg_id = safe_int_format(prescription.get('registrationID'), 0)
                    patient_name = safe_str_format(prescription.get('patient_name'), '未知患者', 8)
                    patient_age = safe_int_format(prescription.get('patient_age'), 0)
                    doctor_name = safe_str_format(prescription.get('doctor_name'), '未知医生', 8)
                    medicine_list = safe_str_format(prescription.get('medicine_list'), '无', 30)
                    total_price = safe_float_format(prescription.get('total_price'), 0.0)

                    print(f"{i:2d}. 处方ID: {reg_id:4d} | "
                          f"患者: {patient_name:8s}({patient_age:2d}岁) | "
                          f"医生: {doctor_name:8s} | "
                          f"药品: {medicine_list:30s} | "
                          f"总价: {total_price:6.1f}元")
            else:
                print(f"ℹ️  没有{status_name}处方")
        else:
            print(f"❌ 获取处方失败: {data.get('message')}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")


def test_dispense_prescription():
    """测试配药操作"""
    print("\n--- 配药操作 ---")
    headers = get_headers()
    if not headers:
        return

    # 先显示待配药处方
    test_get_pending_prescriptions()

    registration_id = input("请输入要配药的处方ID: ").strip()
    if not registration_id:
        print("❌ 处方ID不能为空")
        return

    try:
        response = requests.post(
            f"{BASE_URL}/pharmacy/prescriptions/{registration_id}/dispense",
            headers=headers,
            json={},
            timeout=10
        )
        data = response.json()

        if data.get('code') == 200:
            result_data = data.get('data', {})
            print("✅ 配药成功！")
            print(f"   处方ID: {result_data.get('registrationId')}")
            print(f"   药品清单: {result_data.get('medicineList')}")
            print(f"   总价: {result_data.get('totalPrice')}元")

            dispensed_medicines = result_data.get('dispensedMedicines', [])
            if dispensed_medicines:
                print("   详细清单:")
                for med in dispensed_medicines:
                    medicine_name = safe_str_format(med.get('medicine_name'), '未知药品')
                    amount = safe_int_format(med.get('amount'), 0)
                    price = safe_float_format(med.get('price'), 0.0)
                    unit_price = price / amount if amount > 0 else 0
                    print(f"     - {medicine_name} x{amount} (单价:{unit_price:.1f}元)")
        else:
            print(f"❌ 配药失败: {data.get('message')}")
            error_data = data.get('data', {})
            insufficient_medicines = error_data.get('insufficientMedicines', [])
            if insufficient_medicines:
                print("   缺货药品:")
                for med in insufficient_medicines:
                    medicine_name = safe_str_format(med.get('medicine_name'), '未知药品')
                    required = safe_int_format(med.get('required'), 0)
                    current = safe_int_format(med.get('current'), 0)
                    print(f"     - {medicine_name}: 需要{required}，库存{current}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")


def test_take_medicine():
    """测试取药操作"""
    print("\n--- 取药操作 ---")
    headers = get_headers()
    if not headers:
        return

    # 先显示已配药处方
    test_get_ready_prescriptions()

    registration_id = input("请输入要取药的处方ID: ").strip()
    if not registration_id:
        print("❌ 处方ID不能为空")
        return

    try:
        response = requests.post(
            f"{BASE_URL}/pharmacy/prescriptions/{registration_id}/take",
            headers=headers,
            json={},
            timeout=10
        )
        data = response.json()

        if data.get('code') == 200:
            result_data = data.get('data', {})
            print("✅ 取药成功！")
            print(f"   处方ID: {result_data.get('registrationId')}")
            print(f"   药品清单: {result_data.get('medicineList')}")
            print(f"   总价: {result_data.get('totalPrice')}元")
        else:
            print(f"❌ 取药失败: {data.get('message')}")

    except Exception as e:
        print(f"❌ 发生错误: {e}")


def test_complete_workflow():
    """完整工作流程测试"""
    print("\n--- 完整药房工作流程测试 ---")
    headers = get_headers()
    if not headers:
        return

    # 1. 查看待配药处方
    print("\n步骤1: 查看待配药处方")
    test_get_pending_prescriptions()

    # 2. 选择处方进行配药
    print("\n步骤2: 配药操作")
    registration_id = input("请输入要配药的处方ID: ").strip()
    if not registration_id:
        print("❌ 处方ID不能为空")
        return

    # 执行配药
    try:
        print(f"\n🔄 正在为处方 {registration_id} 执行配药操作...")
        response = requests.post(
            f"{BASE_URL}/pharmacy/prescriptions/{registration_id}/dispense",
            headers=headers,
            json={},
            timeout=10
        )
        dispense_data = response.json()

        if dispense_data.get('code') == 200:
            result_data = dispense_data.get('data', {})
            print("✅ 配药成功！")
            print("📋 配药结果详情:")
            print(f"   📍 处方ID: {result_data.get('registrationId')}")
            print(f"   💊 药品清单: {result_data.get('medicineList')}")
            print(f"   💰 总价格: {result_data.get('totalPrice')}元")

            # 显示详细药品信息
            dispensed_medicines = result_data.get('dispensedMedicines', [])
            if dispensed_medicines:
                print("   📦 详细配药清单:")
                total_amount = 0
                for i, medicine in enumerate(dispensed_medicines, 1):
                    medicine_name = safe_str_format(medicine.get('medicine_name'), '未知药品')
                    amount = safe_int_format(medicine.get('amount'), 0)
                    price = safe_float_format(medicine.get('price'), 0.0)
                    unit_price = price / amount if amount > 0 else 0
                    total_amount += amount

                    print(f"      {i}. {medicine_name}")
                    print(f"         数量: {amount}")
                    print(f"         单价: {unit_price:.2f}元")
                    print(f"         小计: {price:.2f}元")

                print(f"   📊 总计: {len(dispensed_medicines)}种药品，{total_amount}件")
            else:
                print("   ℹ️ 无详细药品信息")

        else:
            print(f"❌ 配药失败: {dispense_data.get('message')}")
            error_data = dispense_data.get('data', {})
            insufficient_medicines = error_data.get('insufficientMedicines', [])
            if insufficient_medicines:
                print("   📉 缺货药品详情:")
                for i, medicine in enumerate(insufficient_medicines, 1):
                    medicine_name = safe_str_format(medicine.get('medicine_name'), '未知药品')
                    required = safe_int_format(medicine.get('required'), 0)
                    current = safe_int_format(medicine.get('current'), 0)
                    print(f"      {i}. {medicine_name}: 需要{required}，库存{current}，缺货{required - current}")
            return

    except Exception as e:
        print(f"❌ 配药错误: {e}")
        return

    # 3. 查看已配药处方
    print("\n步骤3: 查看已配药处方")
    test_get_ready_prescriptions()

    # 4. 执行取药操作
    print("\n步骤4: 取药操作")
    try:
        print(f"\n🔄 正在为处方 {registration_id} 执行取药操作...")
        response = requests.post(
            f"{BASE_URL}/pharmacy/prescriptions/{registration_id}/take",
            headers=headers,
            json={},
            timeout=10
        )
        take_data = response.json()

        if take_data.get('code') == 200:
            result_data = take_data.get('data', {})
            print("✅ 取药成功！")
            print("📋 取药结果详情:")
            print(f"   📍 处方ID: {result_data.get('registrationId')}")
            print(f"   💊 药品清单: {result_data.get('medicineList')}")
            print(f"   💰 总价格: {result_data.get('totalPrice')}元")
            print(f"   ✅ 取药状态: 已完成")

            # 显示取药确认信息
            print("\n🎉 取药流程完成！")
            print("   📝 患者已成功领取所有药品")
            print("   💡 处方状态已更新为'已取药'")

        else:
            print(f"❌ 取药失败: {take_data.get('message')}")
            return

    except Exception as e:
        print(f"❌ 取药错误: {e}")
        return

    # 5. 查看已取药处方
    print("\n步骤5: 查看已取药处方")
    test_get_completed_prescriptions()

    # 6. 显示完整流程总结
    print("\n" + "=" * 60)
    print("📊 完整工作流程总结")
    print("=" * 60)
    print(f"📍 处理的处方ID: {registration_id}")
    print("🔄 执行的操作:")
    print("   ✅ 配药操作 - 成功")
    print("   ✅ 取药操作 - 成功")
    print("📈 状态变化:")
    print("   待配药 → 已配药 → 已取药")
    print("🎯 最终结果:")
    print("   处方流程完整结束，患者已领取药品")
    print("=" * 60)
    print("\n🎉 完整药房工作流程执行完成！")


def main():
    """主函数"""
    print("药房接口集成测试系统")
    print("请确保服务器正在 http://localhost:5000 运行")

    while True:
        print_menu()
        choice = input("请选择操作 (0-10): ").strip()

        if choice == '0':
            print("感谢使用，再见！")
            break
        elif choice == '1':
            login()
        elif choice == '2':
            test_get_all_medicines()
        elif choice == '3':
            test_get_pending_prescriptions()
        elif choice == '4':
            test_get_ready_prescriptions()
        elif choice == '5':
            test_get_completed_prescriptions()
        elif choice == '6':
            test_get_prescriptions_by_state()
        elif choice == '7':
            test_dispense_prescription()
        elif choice == '8':
            test_take_medicine()
        elif choice == '10':
            test_complete_workflow()
        else:
            print("❌ 无效选择，请重新输入！")

        input("\n按回车键继续...")


if __name__ == "__main__":
    main()