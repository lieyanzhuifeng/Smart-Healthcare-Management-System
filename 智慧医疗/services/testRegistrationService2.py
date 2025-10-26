import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.RegistrationService import RegistrationService

#测试未预约患者挂号功能
def test_register_without_appointment():

    service = RegistrationService()

    # 测试数据 - 使用有排班的科室和时间
    patients_id = 1
    office_id = 1  # 医生2的科室ID
    datetime_str = "2025-10-26 21:30:00"  # 有排班的时间

    print(f"🔍 测试未预约挂号 - 患者ID: {patients_id}, 科室ID: {office_id}, 时间: {datetime_str}")

    success, section_id = service.register_without_appointment(patients_id, office_id, datetime_str)

    if success:
        print(f"✅ 挂号成功! sectionID: {section_id}")

        # 验证挂号结果
        details = service.get_registration_details(patients_id, section_id)
        print(f"📋 挂号详情: {details}")
    else:
        print("❌ 挂号失败")


if __name__ == "__main__":
    test_register_without_appointment()