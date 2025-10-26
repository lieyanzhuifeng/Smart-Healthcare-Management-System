import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.RegistrationService import RegistrationService


def test_get_patient_registrations():
    """测试功能12: 获取患者所有挂号信息"""
    print("测试功能12: 获取患者所有挂号信息")
    print("输入: patientsID = 1")

    # 初始化服务
    registration_service = RegistrationService()

    # 调用功能12
    result = registration_service.get_patient_registrations(1)

    print("返回结果:")
    print(result)


if __name__ == "__main__":
    test_get_patient_registrations()