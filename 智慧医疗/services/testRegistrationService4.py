import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.RegistrationService import RegistrationService
import json


def test_get_registration_details():
    """测试功能11: 获取挂号详情 - 基于实际表数据"""
    print("=" * 60)
    print("测试功能11: 获取挂号详情")
    print("基于registration表实际数据构造测试用例")
    print("=" * 60)

    # 初始化服务
    registration_service = RegistrationService()

    # 基于实际表数据构造测试用例
    test_cases = [
        {
            "case_id": 1,
            "description": "患者1在排班1的挂号记录 - 状态1(就诊中)",
            "patient_id": 1,
            "section_id": 1,
            "expected_number": 1,
            "expected_state": 1
        },
        {
            "case_id": 2,
            "description": "患者1在排班2的挂号记录 - 状态0(已挂号/待就诊)",
            "patient_id": 1,
            "section_id": 2,
            "expected_number": 1,
            "expected_state": 0
        }
    ]

    print(f"📋 基于registration表的测试用例:")
    print("patientsID | sectionID | number | state | registrationID")
    print("1         | 1         | 1      | 1     | 1")
    print("1         | 2         | 1      | 0     | 2")
    print()

    # 执行测试用例
    for test_case in test_cases:
        print(f"\n🔍 测试用例 {test_case['case_id']}: {test_case['description']}")
        print("-" * 50)

        print(f"输入参数:")
        print(f"  patientsID: {test_case['patient_id']}")
        print(f"  sectionID: {test_case['section_id']}")

        # 调用功能11
        result = registration_service.get_registration_details(
            test_case['patient_id'],
            test_case['section_id']
        )

        print(f"\n返回结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # 验证结果
        print(f"\n✅ 验证结果:")
        if "error" in result:
            print(f"  ❌ 失败: {result['error']}")
        else:
            # 验证必填字段存在
            required_fields = ['doctor_details', 'number', 'roomID', 'state']
            missing_fields = [field for field in required_fields if field not in result]

            if missing_fields:
                print(f"  ❌ 缺少必填字段: {missing_fields}")
            else:
                print(f"  ✅ 字段完整性: 所有必填字段都存在")

                # 验证具体值
                number_match = result.get('number') == test_case['expected_number']
                state_match = result.get('state') == test_case['expected_state']

                print(
                    f"  📝 挂号号码: {result.get('number')} (期望: {test_case['expected_number']}) - {'✅' if number_match else '❌'}")
                print(
                    f"  📝 挂号状态: {result.get('state')} (期望: {test_case['expected_state']}) - {'✅' if state_match else '❌'}")
                print(f"  📝 房间号: {result.get('roomID')}")
                print(f"  📝 医生信息: {'有' if result.get('doctor_details') else '无'}")

                if number_match and state_match:
                    print(f"  🎉 测试用例 {test_case['case_id']} 通过!")
                else:
                    print(f"  💥 测试用例 {test_case['case_id']} 失败!")


def test_edge_cases():
    """测试边界情况"""
    print("\n" + "=" * 60)
    print("边界情况测试")
    print("=" * 60)

    registration_service = RegistrationService()

    edge_cases = [
        {
            "description": "不存在的患者ID",
            "patient_id": 999,
            "section_id": 1
        },
        {
            "description": "不存在的排班ID",
            "patient_id": 1,
            "section_id": 999
        },
        {
            "description": "患者和排班都不存在",
            "patient_id": 999,
            "section_id": 999
        },
        {
            "description": "患者存在但未在该排班挂号",
            "patient_id": 1,
            "section_id": 3  # 假设患者1没有在排班3挂号
        }
    ]

    for case in edge_cases:
        print(f"\n🔍 边界测试: {case['description']}")
        print("-" * 40)

        print(f"输入: patientsID={case['patient_id']}, sectionID={case['section_id']}")

        result = registration_service.get_registration_details(
            case['patient_id'],
            case['section_id']
        )

        print(f"返回结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if "error" in result:
            print(f"✅ 预期返回错误信息: {result['error']}")
        else:
            print(f"⚠️  未返回错误信息，请检查逻辑")


def test_function_11_integration():
    """功能11集成测试 - 结合其他功能"""
    print("\n" + "=" * 60)
    print("功能11集成测试")
    print("=" * 60)

    registration_service = RegistrationService()

    # 测试场景：先获取患者所有挂号，再查看每个挂号的详情
    print("🔍 测试场景: 查看患者1的所有挂号详情")
    print("-" * 40)

    patient_id = 1

    # 先获取患者所有挂号信息（功能12）
    print(f"步骤1: 获取患者{patient_id}的所有挂号信息")
    all_registrations = registration_service.get_patient_registrations(patient_id)
    print(f"患者{patient_id}共有 {len(all_registrations)} 条挂号记录")

    # 然后查看每条挂号的详情（功能11）
    for i, reg in enumerate(all_registrations, 1):
        section_id = reg.get('sectionID')
        if section_id:
            print(f"\n步骤2.{i}: 查看挂号详情 - sectionID={section_id}")
            details = registration_service.get_registration_details(patient_id, section_id)

            if "error" not in details:
                print(f"  ✅ 挂号详情获取成功")
                print(f"    号码: {details.get('number')}, 状态: {details.get('state')}, 房间: {details.get('roomID')}")
            else:
                print(f"  ❌ 获取详情失败: {details.get('error')}")


if __name__ == "__main__":
    print("开始测试功能11: 获取挂号详情")
    print("基于实际registration表数据:")
    print("+-----------+-----------+--------+-------+-----------------+")
    print("| patientsID| sectionID | number | state | registrationID |")
    print("+-----------+-----------+--------+-------+-----------------+")
    print("|     1     |     1     |   1    |   1   |       1         |")
    print("|     1     |     2     |   1    |   0   |       2         |")
    print("+-----------+-----------+--------+-------+-----------------+")
    print()

    # 运行主要测试
    test_get_registration_details()

    # 运行边界测试
    test_edge_cases()

    # 运行集成测试
    test_function_11_integration()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)