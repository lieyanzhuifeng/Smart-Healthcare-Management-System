import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Any, Optional
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repository.doctor import DoctorRepository
from model import Doctor


def test_doctor_repository_basic():
    """测试医生Repository基本功能"""
    print("🧪 开始测试医生Repository...")

    try:
        # 1. 初始化医生Repository
        print("1. 初始化医生Repository...")
        doctor_repo = DoctorRepository()
        print("✅ 医生Repository初始化成功")

        # 2. 测试获取所有医生
        print("\n2. 测试获取所有医生...")
        doctors = doctor_repo.get_all_doctors()
        print(f"✅ 获取到 {len(doctors)} 名医生")

        # 显示医生信息 - 现在使用对象属性而不是字典键
        if doctors:
            print("\n📋 医生列表:")
            for i, doctor in enumerate(doctors, 1):
                print(f"   {i}. ID: {doctor.doctorID}, 姓名: {doctor.name}, "
                      f"年龄: {doctor.age}, 科室ID: {doctor.officeID}")

        # 3. 测试根据ID获取医生
        print("\n3. 测试根据ID获取医生...")
        if doctors:
            test_doctor_id = doctors[0].doctorID
            doctor_by_id = doctor_repo.get_doctor_by_id(test_doctor_id)

            if doctor_by_id:
                print(f"✅ 成功获取医生: {doctor_by_id.name} (ID: {doctor_by_id.doctorID})")
                print(f"   详细信息: 专长ID: {doctor_by_id.expertiseID}, "
                      f"职位ID: {doctor_by_id.positionID}, "
                      f"患者数量: {doctor_by_id.NumberOfPatients}")
            else:
                print("❌ 根据ID获取医生失败")

        # 4. 测试根据科室获取医生
        print("\n4. 测试根据科室获取医生...")
        if doctors:
            # 获取一个存在的科室ID
            office_id = doctors[0].officeID
            office_doctors = doctor_repo.get_doctors_by_office(office_id)

            print(f"✅ 科室 {office_id} 下有 {len(office_doctors)} 名医生")

            if office_doctors:
                doctor_names = [doc.name for doc in office_doctors]
                print(f"   该科室医生: {', '.join(doctor_names)}")

        # 5. 测试更新医生患者数量
        print("\n5. 测试更新医生患者数量...")
        if doctors:
            test_doctor = doctors[0]
            original_count = test_doctor.NumberOfPatients
            new_count = original_count + 1

            success = doctor_repo.update_doctor_patient_count(test_doctor.doctorID, new_count)
            if success:
                print(f"✅ 成功更新医生患者数量: {original_count} → {new_count}")

                # 验证更新
                updated_doctor = doctor_repo.get_doctor_by_id(test_doctor.doctorID)
                if updated_doctor and updated_doctor.NumberOfPatients == new_count:
                    print("✅ 患者数量更新验证成功")
                else:
                    print("❌ 患者数量更新验证失败")
            else:
                print("❌ 更新医生患者数量失败")

        # 6. 测试创建医生
        print("\n6. 测试创建医生...")
        new_doctor = Doctor(
            doctorID=100,  # ID由数据库自动生成
            name="测试医生",
            age=35,
            expertiseID=1,
            officeID=1,
            positionID=1,
            NumberOfPatients=0
        )

        success = doctor_repo.create_doctor(new_doctor)
        if success:
            print("✅ 创建医生成功")
        else:
            print("❌ 创建医生失败")

        print("\n🎉 医生Repository测试完成！")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_doctor_advanced():
    """测试医生Repository高级功能"""
    print("\n🔬 开始高级功能测试...")

    try:
        doctor_repo = DoctorRepository()

        # 获取所有医生信息（包含关联信息）
        doctors = doctor_repo.get_all_doctors()

        if doctors:
            print("📊 医生详细信息:")
            for doctor in doctors[:3]:  # 只显示前3个医生
                print(f"\n👨‍⚕️ 医生: {doctor.name}")
                print(f"   ID: {doctor.doctorID}")
                print(f"   年龄: {doctor.age}")
                print(f"   专长ID: {doctor.expertiseID}")
                print(f"   科室ID: {doctor.officeID}")
                print(f"   职位ID: {doctor.positionID}")
                print(f"   患者数量: {doctor.NumberOfPatients}")

                # 注意：现在关联信息不再直接包含在Doctor对象中
                # 如果需要关联信息，需要单独查询或修改get_all_doctors方法

        print(f"\n📈 统计信息:")
        print(f"   医生总数: {len(doctors)}")

        # 按科室统计
        office_counts = {}
        for doctor in doctors:
            office_id = doctor.officeID
            office_counts[office_id] = office_counts.get(office_id, 0) + 1

        print(f"   科室分布: {office_counts}")

        # 测试根据专业领域获取医生
        print("\n7. 测试根据专业领域获取医生...")
        if doctors:
            expertise_id = doctors[0].expertiseID
            expertise_doctors = doctor_repo.get_doctors_by_expertise(expertise_id)
            print(f"✅ 专长领域 {expertise_id} 下有 {len(expertise_doctors)} 名医生")

    except Exception as e:
        print(f"❌ 高级功能测试失败: {e}")


def test_doctor_model_features():
    """测试Doctor模型的特性"""
    print("\n🔍 测试Doctor模型特性...")

    try:
        # 测试from_dict方法
        doctor_data = {
            'doctorID': 1,
            'name': '测试医生',
            'age': 40,
            'expertiseID': 2,
            'officeID': 3,
            'positionID': 1,
            'NumberOfPatients': 10
        }

        doctor = Doctor.from_dict(doctor_data)
        print("✅ from_dict方法测试成功")
        print(f"   创建的医生: {doctor.name}, ID: {doctor.doctorID}")

        # 测试对象属性访问
        print(f"   年龄: {doctor.age}")
        print(f"   专长ID: {doctor.expertiseID}")
        print(f"   患者数量: {doctor.NumberOfPatients}")

        # 测试dataclass的自动功能
        print(f"   字符串表示: {doctor}")

        # 测试相等性比较
        doctor2 = Doctor.from_dict(doctor_data)
        print(f"   相等性比较: {doctor == doctor2}")

    except Exception as e:
        print(f"❌ 模型特性测试失败: {e}")


if __name__ == "__main__":
    # 运行基本功能测试
    test_doctor_repository_basic()

    # 运行高级功能测试
    test_doctor_advanced()

    # 运行模型特性测试
    test_doctor_model_features()