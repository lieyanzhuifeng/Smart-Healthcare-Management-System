import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.DoctorScheduleService import DoctorScheduleService


def test_generate_and_save():
    """简单测试 generate_and_save_schedules 函数"""
    print("测试 generate_and_save_schedules 函数")
    print("日期范围: 2025-10-27 到 2025-10-27")

    # 初始化服务
    schedule_service = DoctorScheduleService()

    # 直接调用函数
    success = schedule_service.generate_and_save_schedules(
        start_date="2025-10-30",
        end_date="2025-10-30",
        timeslots=[3]
    )

    print(f"结果: {'✅ 成功' if success else '❌ 失败'}")


if __name__ == "__main__":
    test_generate_and_save()