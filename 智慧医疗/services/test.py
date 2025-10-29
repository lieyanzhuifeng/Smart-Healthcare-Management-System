# test_simple_service.py
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.RegistrationService import RegistrationService


def test_simple():
    """简单测试services层预约转挂号"""
    print("🔧 简单测试Services层预约转挂号")

    try:
        service = RegistrationService()
        patient_id = 1
        section_id = 224

        print(f"测试: 患者 {patient_id} 将排班 {section_id} 的预约转为挂号")

        # 直接测试预约转挂号
        result = service.register_with_appointment(patient_id, section_id)

        print(f"结果: {result}")

        if result:
            print("✅ Services层预约转挂号成功！")
        else:
            print("❌ Services层预约转挂号失败")

        return result

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    test_simple()