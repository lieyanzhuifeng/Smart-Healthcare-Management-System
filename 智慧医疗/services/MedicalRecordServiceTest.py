import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.MedicalRecordService import MedicalRecordService


def test_medical_record_service():
    """测试医疗记录服务"""
    print("=== 医疗记录服务测试 ===")

    try:
        medical_service = MedicalRecordService()
        print("✅ 服务初始化成功")

    except Exception as e:
        print(f"❌ 服务初始化失败: {e}")
        return

    while True:
        print("\n请选择测试功能：")
        print("1. 查询患者病历")
        print("2. 查询处方详情")
        print("3. 查询病历摘要统计")
        print("5. 退出测试")

        choice = input("请输入选择 (1-5): ").strip()

        if choice == '1':
            try:
                patient_id = input("请输入患者ID: ").strip()
                if not patient_id:
                    print("错误：请输入患者ID")
                    continue

                patient_id = int(patient_id)
                print(f"\n查询患者 {patient_id} 的病历记录...")
                records = medical_service.get_patient_medical_records(patient_id)

                if records:
                    print(f"✅ 找到 {len(records)} 条病历记录:")
                    for i, record in enumerate(records, 1):
                        print(f"\n--- 第 {i} 条病历 ---")
                        print(f"病历ID: {record['registrationID']}")
                        print(f"就诊时间: {record['time']}")
                        print(f"诊断信息: {record['information']}")
                        print(f"是否有药品: {'是' if record['have_medicine'] else '否'}")

                        doctor = record['doctor']
                        print(f"主治医生: {doctor.doctor_name}")
                        print(f"医生ID: {doctor.doctorID}")
                        print(f"年龄: {doctor.age}")
                        print(f"科室: {doctor.office_name}")
                        print(f"专业: {doctor.expertise_name}")
                        print(f"职称: {doctor.position_name}")
                        print(f"患者数量: {doctor.NumberOfPatients}")

                        # 处方信息
                        prescription = record['prescription']
                        if prescription:
                            print("处方药品:")
                            for item in prescription:
                                medicine = item['medicine']
                                order = item['order']
                                print(f"  - {medicine.name}: {order.amount}盒, 总价: {order.price}元")
                else:
                    print("❌ 未找到该患者的病历记录")

            except ValueError:
                print("❌ 错误：患者ID必须是数字")
            except Exception as e:
                print(f"❌ 查询患者病历时出错: {e}")

        elif choice == '2':
            try:
                registration_id = input("请输入病历ID: ").strip()
                if not registration_id:
                    print("错误：请输入病历ID")
                    continue

                registration_id = int(registration_id)
                print(f"\n查询病历 {registration_id} 的处方详情...")
                prescription = medical_service.get_prescription_details(registration_id)

                if prescription:
                    print(f"✅ 找到 {len(prescription)} 种药品:")
                    total_price = 0
                    for i, item in enumerate(prescription, 1):
                        medicine = item.get('medicine')
                        order = item.get('order')
                        if medicine and order:
                            total_price += order.price

                            print(f"\n{i}. 药品信息:")
                            print(f"   药品ID: {medicine.medicineID}")
                            print(f"   药品名称: {medicine.name}")
                            print(f"   单价: {medicine.price} 元")
                            print(f"   描述: {medicine.description}")
                            print(f"   订单信息:")
                            print(f"     订单ID: {order.orderID}")
                            print(f"     数量: {order.amount}")
                            print(f"     总价: {order.price} 元")

                    print(f"\n💰 处方总价: {total_price} 元")
                else:
                    print("❌ 该病历没有处方信息")

            except ValueError:
                print("❌ 错误：病历ID必须是数字")
            except Exception as e:
                print(f"❌ 查询处方详情时出错: {e}")

        elif choice == '3':
            try:
                patient_id = input("请输入患者ID: ").strip()
                if not patient_id:
                    print("错误：请输入患者ID")
                    continue

                patient_id = int(patient_id)
                print(f"\n📊 查询患者 {patient_id} 的病历摘要统计...")
                summary = medical_service.get_medical_record_summary(patient_id)

                if summary:
                    print("📈 病历摘要统计结果:")
                    print(f"👤 患者ID: {summary.get('patient_id')}")
                    print(f"📋 总病历数: {summary.get('total_records')}")
                    print(f"💊 带处方病历数: {summary.get('records_with_medicine')}")

                    # 计算不带处方的病历数
                    without_medicine = summary.get('total_records', 0) - summary.get('records_with_medicine', 0)
                    print(f"📝 不带处方病历数: {without_medicine}")

                    # 计算处方率
                    if summary.get('total_records', 0) > 0:
                        prescription_rate = (summary.get('records_with_medicine', 0) / summary.get('total_records',
                                                                                                   0)) * 100
                        print(f"📊 处方率: {prescription_rate:.1f}%")

                    print(f"🕒 最近就诊时间: {summary.get('recent_record_time')}")
                    print(f"👨‍⚕️ 最近就诊医生: {summary.get('recent_doctor', '无记录')}")
                else:
                    print("❌ 未找到该患者的病历摘要")

            except ValueError:
                print("❌ 错误：患者ID必须是数字")
            except Exception as e:
                print(f"❌ 查询病历摘要时出错: {e}")

        elif choice == '5':
            print("退出测试程序")
            break

        else:
            print("❌ 无效选择，请重新输入")


def quick_statistics_test():
    """快速统计测试"""
    print("\n=== 快速统计测试 ===")

    try:
        medical_service = MedicalRecordService()
        print("✅ 服务初始化成功")

        # 让用户输入测试数据
        patient_id = input("请输入患者ID进行统计测试: ").strip()
        if patient_id:
            patient_id = int(patient_id)

            print(f"\n🧪 对患者 {patient_id} 进行综合统计测试...")

            # 测试病历摘要统计
            print("\n1. 病历摘要统计:")
            summary = medical_service.get_medical_record_summary(patient_id)
            if summary:
                print(f"   总病历数: {summary.get('total_records')}")
                print(f"   带处方病历数: {summary.get('records_with_medicine')}")
                print(f"   最近就诊医生: {summary.get('recent_doctor')}")

                # 如果有病历记录，测试处方统计
                records = medical_service.get_patient_medical_records(patient_id)
                if records:
                    # 找到有处方的病历
                    for record in records:
                        if record['have_medicine']:
                            registration_id = record['registrationID']
                            print(f"\n2. 病历 {registration_id} 的处方详情:")
                            prescription_details = medical_service.get_prescription_details(registration_id)
                            if prescription_details:
                                total_medicines = len(prescription_details)
                                total_price = sum(item['order'].price for item in prescription_details)
                                print(f"   药品数量: {total_medicines}")
                                print(f"   处方总价: {total_price} 元")
                            break
            else:
                print("   无病历记录")

        print("\n✅ 快速统计测试完成！")

    except Exception as e:
        print(f"❌ 快速统计测试失败: {e}")


if __name__ == "__main__":
    print("选择测试模式:")
    print("1. 完整交互测试")
    print("2. 快速统计测试")

    mode = input("请选择模式 (1 或 2): ").strip()

    if mode == '1':
        test_medical_record_service()
    elif mode == '2':
        quick_statistics_test()
    else:
        print("无效选择")