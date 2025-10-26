import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Any, Optional
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repository.patient import PatientRepository
from model import Patient


def test_patient_repository_integration():
    """测试患者Repository集成功能"""
    print("🧪 开始测试患者Repository集成功能...")

    try:
        # 1. 初始化患者Repository
        print("1. 初始化患者Repository...")
        patient_repo = PatientRepository()
        print("✅ 患者Repository初始化成功")

        # 2. 测试获取所有患者
        print("\n2. 测试获取所有患者...")
        patients = patient_repo.get_all_patients()
        print(f"✅ 获取到 {len(patients)} 名患者")

        # 显示患者信息
        if patients:
            print("\n📋 患者列表:")
            for i, patient in enumerate(patients, 1):
                print(f"   {i}. ID: {patient.patientsID}, 姓名: {patient.name}, 年龄: {patient.age}")

        # 3. 测试根据ID获取患者
        print("\n3. 测试根据ID获取患者...")
        if patients:
            test_patient_id = patients[0].patientsID
            patient_by_id = patient_repo.get_patient_by_id(test_patient_id)

            if patient_by_id:
                print(f"✅ 成功获取患者: {patient_by_id.name} (ID: {patient_by_id.patientsID})")
                print(f"   详细信息: 姓名: {patient_by_id.name}, 年龄: {patient_by_id.age}")
            else:
                print("❌ 根据ID获取患者失败")

        # 4. 测试创建新患者
        print("\n4. 测试创建新患者...")
        success = patient_repo.create_patient("集成测试患者", 28)
        if success:
            print("✅ 创建患者成功")

            # 验证新患者是否创建成功
            new_patients = patient_repo.get_all_patients()
            test_patient = None
            for patient in new_patients:
                if patient.name == "集成测试患者" and patient.age == 28:
                    test_patient = patient
                    break

            if test_patient:
                print(f"✅ 验证新患者创建成功: {test_patient.name} (ID: {test_patient.patientsID})")

                # 5. 测试更新患者信息
                print("\n5. 测试更新患者信息...")
                update_success = patient_repo.update_patient(
                    test_patient.patientsID, "更新后的患者", 30
                )
                if update_success:
                    print("✅ 更新患者信息成功")

                    # 验证更新
                    updated_patient = patient_repo.get_patient_by_id(test_patient.patientsID)
                    if updated_patient and updated_patient.name == "更新后的患者" and updated_patient.age == 30:
                        print("✅ 患者信息更新验证成功")
                    else:
                        print("❌ 患者信息更新验证失败")
                else:
                    print("❌ 更新患者信息失败")

                # 6. 测试删除患者
                print("\n6. 测试删除患者...")
                delete_success = patient_repo.delete_patient(test_patient.patientsID)
                if delete_success:
                    print("✅ 删除患者成功")

                    # 验证删除
                    deleted_patient = patient_repo.get_patient_by_id(test_patient.patientsID)
                    if deleted_patient is None:
                        print("✅ 患者删除验证成功")
                    else:
                        print("❌ 患者删除验证失败")
                else:
                    print("❌ 删除患者失败")
            else:
                print("❌ 新患者创建验证失败")
        else:
            print("❌ 创建患者失败")

        # 7. 测试搜索患者
        print("\n7. 测试搜索患者...")
        if patients:
            # 使用现有患者的姓名进行搜索
            search_name = patients[0].name
            search_results = patient_repo.search_patients_by_name(search_name)
            print(f"✅ 搜索 '{search_name}' 找到 {len(search_results)} 名患者")

            if search_results:
                for patient in search_results:
                    print(f"   - {patient.name} (ID: {patient.patientsID}, 年龄: {patient.age})")

        # 8. 测试按年龄范围查询
        print("\n8. 测试按年龄范围查询...")
        age_range_patients = patient_repo.get_patients_by_age_range(20, 40)
        print(f"✅ 年龄20-40岁的患者有 {len(age_range_patients)} 名")

        if age_range_patients:
            for patient in age_range_patients[:3]:  # 只显示前3个
                print(f"   - {patient.name} (年龄: {patient.age})")

        print("\n🎉 患者Repository集成测试完成！")

    except Exception as e:
        print(f"\n❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_patient_model_features():
    """测试Patient模型特性"""
    print("\n🔍 测试Patient模型特性...")

    try:
        # 测试from_dict方法
        patient_data = {
            'patientsID': 999,
            'name': '测试患者',
            'age': 35
        }

        patient = Patient.from_dict(patient_data)
        print("✅ from_dict方法测试成功")
        print(f"   创建的患者: {patient.name}, ID: {patient.patientsID}, 年龄: {patient.age}")

        # 测试对象属性访问
        print(f"   姓名: {patient.name}")
        print(f"   年龄: {patient.age}")
        print(f"   ID: {patient.patientsID}")

        # 测试dataclass的自动功能
        print(f"   字符串表示: {patient}")

        # 测试相等性比较
        patient2 = Patient.from_dict(patient_data)
        print(f"   相等性比较: {patient == patient2}")

        # 测试修改属性
        patient.name = "修改后的姓名"
        print(f"   修改后姓名: {patient.name}")

        print("✅ Patient模型特性测试完成")

    except Exception as e:
        print(f"❌ 模型特性测试失败: {e}")


def test_patient_statistics():
    """测试患者统计信息"""
    print("\n📊 测试患者统计信息...")

    try:
        patient_repo = PatientRepository()
        patients = patient_repo.get_all_patients()

        if patients:
            print(f"患者总数: {len(patients)}")

            # 年龄统计
            age_groups = {
                "儿童(0-18)": 0,
                "青年(19-35)": 0,
                "中年(36-60)": 0,
                "老年(61+)": 0
            }

            for patient in patients:
                if patient.age <= 18:
                    age_groups["儿童(0-18)"] += 1
                elif patient.age <= 35:
                    age_groups["青年(19-35)"] += 1
                elif patient.age <= 60:
                    age_groups["中年(36-60)"] += 1
                else:
                    age_groups["老年(61+)"] += 1

            print("年龄分布:")
            for group, count in age_groups.items():
                if count > 0:
                    percentage = (count / len(patients)) * 100
                    print(f"  {group}: {count}人 ({percentage:.1f}%)")

            # 平均年龄
            avg_age = sum(patient.age for patient in patients) / len(patients)
            print(f"平均年龄: {avg_age:.1f}岁")

            # 最年长和最年轻
            oldest = max(patients, key=lambda x: x.age)
            youngest = min(patients, key=lambda x: x.age)
            print(f"最年长: {oldest.name} ({oldest.age}岁)")
            print(f"最年轻: {youngest.name} ({youngest.age}岁)")

    except Exception as e:
        print(f"❌ 统计信息测试失败: {e}")


if __name__ == "__main__":
    # 运行集成测试
    test_patient_repository_integration()

    # 运行模型特性测试
    test_patient_model_features()

    # 运行统计信息测试
    test_patient_statistics()