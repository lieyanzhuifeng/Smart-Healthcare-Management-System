import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.RegistrationService import RegistrationService
from services.AppointmentService import AppointmentService
from repository.office import OfficeRepository
from repository.patient import PatientRepository


def get_user_input(prompt, input_type=str):
    """获取用户输入"""
    try:
        user_input = input(prompt).strip()
        if input_type == int:
            return int(user_input) if user_input else None
        return user_input if user_input else None
    except ValueError:
        print("输入格式错误，请重新输入")
        return None
    except KeyboardInterrupt:
        print("\n用户取消输入")
        return None


def test_patient_registration_flow():
    """患者挂号流程测试"""
    print("=== 患者挂号系统 ===")

    # 创建服务实例
    reg_service = RegistrationService()
    app_service = AppointmentService()
    office_repo = OfficeRepository()
    patient_repo = PatientRepository()

    while True:
        print("\n请选择患者类型:")
        print("1. 未预约患者直接挂号")
        print("2. 预约患者转挂号")
        print("3. 退出系统")

        choice = get_user_input("请输入选择 (1-3): ", int)

        if choice == 1:
            test_no_appointment_patient(reg_service, office_repo, patient_repo)
        elif choice == 2:
            test_appointment_patient(reg_service, app_service, patient_repo)
        elif choice == 3:
            print("感谢使用挂号系统！")
            break
        else:
            print("无效选择，请重新输入")


def test_no_appointment_patient(reg_service, office_repo, patient_repo):
    """未预约患者挂号流程"""
    print("\n=== 未预约患者挂号 ===")

    # 1. 输入患者ID
    patients_id = get_user_input("请输入您的患者ID: ", int)
    if not patients_id:
        print("患者ID不能为空")
        return

    # 验证患者是否存在
    patient = patient_repo.get_patient_by_id(patients_id)
    if not patient:
        print(f"❌ 患者ID {patients_id} 不存在")
        return

    print(f"✅ 验证通过 - 欢迎 {patient.name} 患者")

    # 2. 显示所有科室供选择
    print("\n请选择就诊科室:")
    offices = office_repo.get_all_offices()
    if not offices:
        print("❌ 暂无可用科室")
        return

    for i, office in enumerate(offices, 1):
        print(f"  {i}. {office.name} (科室ID: {office.officeID})")

    # 3. 选择科室
    office_choice = get_user_input(f"请选择科室 (1-{len(offices)}): ", int)
    if not office_choice or office_choice < 1 or office_choice > len(offices):
        print("❌ 无效的科室选择")
        return

    selected_office = offices[office_choice - 1]
    office_id = selected_office.officeID
    print(f"✅ 已选择科室: {selected_office.name}")

    # 4. 使用当前时间进行挂号
    current_time = datetime.now()
    date_str = current_time.strftime('%Y-%m-%d')
    time_str = current_time.strftime('%H:%M:%S')
    datetime_str = f"{date_str} {time_str}"

    print(f"\n📅 挂号信息:")
    print(f"   日期: {date_str}")
    print(f"   时间: {time_str}")
    print(f"   科室: {selected_office.name}")

    # 5. 检查当前时间段可用性
    print("\n🔍 检查挂号可用性...")
    availability = reg_service.get_current_timeslot_availability(office_id, datetime_str)

    if "error" in availability:
        print(f"❌ {availability.get('error')}")
        if "available_timeslots" in availability:
            print("   请在其他时间段就诊:")
            for ts in availability["available_timeslots"]:
                print(f"     - {ts}")
        return

    # 显示可用性信息
    timeslot = availability.get('timeslot', {})
    avail_info = availability.get('availability', {})

    print(f"✅ 当前时间段: {timeslot.get('starttime')} - {timeslot.get('endtime')}")
    print(f"   剩余挂号名额: {avail_info.get('restregistration', 0)}")

    if avail_info.get('restregistration', 0) <= 0:
        print("❌ 当前时间段已无挂号名额，请选择其他时间段")
        return

    # 6. 确认挂号
    confirm = get_user_input("确认挂号？(输入 'yes' 确认): ")
    if confirm.lower() != 'yes':
        print("挂号已取消")
        return

    # 7. 执行挂号
    print("\n🔄 正在挂号...")
    success, section_id = reg_service.register_without_appointment(patients_id, office_id, datetime_str)

    # 8. 显示结果
    if success:
        print(f"✅ 挂号成功！")
        print(f"   您的挂号号码: 请查看详情")

        # 显示挂号详情
        details = reg_service.get_registration_details(patients_id, section_id)
        if "error" not in details:
            print(f"\n📋 挂号详情:")
            print(f"   患者: {patient.name}")
            print(f"   挂号号码: {details.get('number')}")
            print(f"   就诊状态: {details.get('state')}")

            if details.get('doctor_details'):
                doctor = details['doctor_details']
                print(f"   接诊医生: {doctor.get('doctor_name')}")
                print(f"   科室: {doctor.get('office_name')}")
                print(f"   专业: {doctor.get('expertise_name')}")

            if details.get('roomID'):
                print(f"   就诊房间: {details.get('roomID')}")
    else:
        print(f"❌ 挂号失败，请稍后重试或联系前台")


def test_appointment_patient(reg_service, app_service, patient_repo):
    """预约患者转挂号流程"""
    print("\n=== 预约患者转挂号 ===")

    # 1. 输入患者ID
    patients_id = get_user_input("请输入您的患者ID: ", int)
    if not patients_id:
        print("患者ID不能为空")
        return

    # 验证患者是否存在
    patient = patient_repo.get_patient_by_id(patients_id)
    if not patient:
        print(f"❌ 患者ID {patients_id} 不存在")
        return

    print(f"✅ 验证通过 - 欢迎 {patient.name} 患者")

    # 2. 获取患者的所有预约信息
    print("\n🔍 查询您的预约记录...")
    appointment_result = app_service.get_patient_appointments(patients_id)

    if not appointment_result.get('success'):
        print(f"❌ 查询预约失败: {appointment_result.get('message')}")
        return

    appointments = appointment_result.get('appointments', [])
    # 过滤有效预约（状态不是cancelled或completed）
    active_appointments = [a for a in appointments if a.get('state') not in ['cancelled', 'completed']]

    if not active_appointments:
        print("❌ 您没有有效的预约记录")
        print("   请先进行预约或选择'未预约患者直接挂号'")
        return

    print(f"✅ 找到 {len(active_appointments)} 个有效预约")

    # 3. 显示有效预约供选择
    print("\n请选择要转为挂号的预约:")
    for i, appointment in enumerate(active_appointments, 1):
        print(f"  {i}. 医生: {appointment.get('doctor_name')}")
        print(f"     科室: {appointment.get('office_name')}")
        print(f"     日期: {appointment.get('date')}")
        print(f"     时间: {appointment.get('starttime')} - {appointment.get('endtime')}")
        print(f"     排班ID: {appointment.get('sectionID')}")
        print()

    # 4. 选择预约
    app_choice = get_user_input(f"请选择预约 (1-{len(active_appointments)}): ", int)
    if not app_choice or app_choice < 1 or app_choice > len(active_appointments):
        print("❌ 无效的预约选择")
        return

    selected_appointment = active_appointments[app_choice - 1]
    section_id = selected_appointment.get('sectionID')

    print(f"✅ 已选择预约:")
    print(f"   医生: {selected_appointment.get('doctor_name')}")
    print(f"   科室: {selected_appointment.get('office_name')}")
    print(f"   时间: {selected_appointment.get('date')} {selected_appointment.get('starttime')}")

    # 5. 检查排班可用性 - 修复：使用正确的方法名
    print("\n🔍 检查排班可用性...")
    availability_result = reg_service.check_appointment_availability(section_id)  # 修复方法名

    if not availability_result.get('is_available', False):
        print("❌ 该排班已无挂号名额")
        return

    # 6. 确认转挂号
    confirm = get_user_input("确认将预约转为挂号？(输入 'yes' 确认): ")
    if confirm.lower() != 'yes':
        print("转挂号已取消")
        return

    # 7. 执行转挂号
    print("\n🔄 正在将预约转为挂号...")
    success = reg_service.register_with_appointment(patients_id, section_id)

    # 8. 显示结果
    if success:
        print(f"✅ 转挂号成功！")

        # 显示挂号详情
        details = reg_service.get_registration_details(patients_id, section_id)
        if "error" not in details:
            print(f"\n📋 挂号详情:")
            print(f"   患者: {patient.name}")
            print(f"   挂号号码: {details.get('number')}")
            print(f"   就诊状态: {details.get('state')}")

            if details.get('doctor_details'):
                doctor = details['doctor_details']
                print(f"   接诊医生: {doctor.get('doctor_name')}")
                print(f"   科室: {doctor.get('office_name')}")

            if details.get('roomID'):
                print(f"   就诊房间: {details.get('roomID')}")
    else:
        print(f"❌ 转挂号失败，请稍后重试或联系前台")


def main():
    """主函数"""
    try:
        test_patient_registration_flow()
    except Exception as e:
        print(f"系统错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
    print("\n挂号系统使用完成！")