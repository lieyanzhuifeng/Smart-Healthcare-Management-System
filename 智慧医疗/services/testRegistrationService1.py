import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.RegistrationService import RegistrationService


def test_current_timeslot_availability():
    """测试获取当前时间段可用性功能"""
    service = RegistrationService()

    # 测试数据 - 使用正确的科室ID
    office_id = 1  # 改为医生2的实际科室ID
    datetime_str = "2025-10-26 21:30:00"

    print(f"🔍 测试 - 科室ID: {office_id}, 时间: {datetime_str}")

    availability = service.get_current_timeslot_availability(office_id, datetime_str)

    if "error" in availability:
        print(f"❌ 结果: {availability['error']}")
    else:
        print(f"✅ 时间段: {availability['timeslot']['starttime']} - {availability['timeslot']['endtime']}")
        print(f"   剩余挂号名额: {availability['availability'].get('restregistration', 'N/A')}")
        print(f"   诊室ID: {availability['availability'].get('roomID', 'N/A')}")
        print(f"   医生数量: {availability['availability'].get('doctor_count', 'N/A')}")


if __name__ == "__main__":
    test_current_timeslot_availability()