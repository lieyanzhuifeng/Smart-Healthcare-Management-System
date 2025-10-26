import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.RegistrationService import RegistrationService


def test_register_with_appointment():
    """测试功能10: 预约患者转挂号"""
    print("测试功能10: 预约患者转挂号")
    print("appointment表数据:")
    print("patientsID | sectionID | state | appointmentID")
    print("1         | 2         | 3     | 2")
    print("1         | 2         | 3     | 3")
    print()

    # 初始化服务
    registration_service = RegistrationService()

    # 测试用例1: 患者1在排班2转挂号
    print("测试用例1: 患者1在排班2转挂号")
    print("输入: patientsID=1, sectionID=2")

    result = registration_service.register_with_appointment(1, 2)

    print("返回结果:", result)
    print()

    # 测试用例2: 不存在的排班
    print("测试用例2: 不存在的排班")
    print("输入: patientsID=1, sectionID=999")

    result = registration_service.register_with_appointment(1, 999)

    print("返回结果:", result)
    print()

    # 测试用例3: 不存在的患者
    print("测试用例3: 不存在的患者")
    print("输入: patientsID=999, sectionID=2")

    result = registration_service.register_with_appointment(999, 2)

    print("返回结果:", result)


if __name__ == "__main__":
    test_register_with_appointment()