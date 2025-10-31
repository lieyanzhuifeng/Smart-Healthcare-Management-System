# api/patient.py
import sys
import os
import json
from datetime import datetime, date, timedelta

# 添加项目路径
sys.path.append('..')
from flask import Blueprint, request, jsonify, Response
from services.AppointmentService import AppointmentService
from services.RegistrationService import RegistrationService
from services.AuthService import AuthService
from services.MedicalRecordService import MedicalRecordService
from repository.office import OfficeRepository
from repository.patient import PatientRepository

bp = Blueprint('patient', __name__)
appointment_service = AppointmentService()
registration_service = RegistrationService()
medical_record_service = MedicalRecordService()
auth_service = AuthService()
office_repo = OfficeRepository()
patient_repo = PatientRepository()


class CustomJSONEncoder(json.JSONEncoder):
    """自定义JSON编码器处理特殊类型"""

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            return str(obj)
        elif hasattr(obj, '__dict__'):
            # 处理对象序列化
            return obj.__dict__
        return super().default(obj)


def get_current_patient_id():
    """从token获取当前患者ID"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None
    user_info = auth_service.verify_token(token)
    return user_info.get('user_id') if user_info and user_info.get('role') == 'patient' else None


def safe_json_response(data, status=200):
    """安全的JSON响应处理"""
    try:
        return jsonify(data)
    except Exception as e:
        # 如果常规序列化失败，使用自定义编码器
        try:
            response_data = json.dumps(data, cls=CustomJSONEncoder, ensure_ascii=False)
            return Response(response_data, mimetype='application/json')
        except Exception as final_error:
            error_response = {
                "code": 500,
                "message": f"数据序列化错误: {str(final_error)}"
            }
            return jsonify(error_response)


@bp.route('/appointments', methods=['GET'])
def get_appointments():
    """获取患者预约列表"""
    patient_id = get_current_patient_id()
    if not patient_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        result = appointment_service.get_patient_appointments(patient_id)
        if result.get('success'):
            appointments = result.get('appointments', [])

            # 构建标准化的响应数据
            response_data = {
                "code": 200,
                "message": "获取预约列表成功",
                "data": {
                    "appointments": appointments,
                    "statistics": result.get('statistics', {})
                }
            }
            return safe_json_response(response_data)
        else:
            return jsonify({
                "code": 500,
                "message": result.get('message', '获取预约失败')
            })
    except Exception as e:
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})


@bp.route('/appointments', methods=['POST'])
def create_appointment():
    """创建预约"""
    patient_id = get_current_patient_id()
    if not patient_id:
        return jsonify({"code": 401, "message": "未认证"})

    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "message": "请求数据不能为空"})

    section_id = data.get('sectionId')
    if not section_id:
        return jsonify({"code": 400, "message": "缺少sectionId参数"})

    try:
        result = appointment_service.create_appointment(patient_id, section_id)
        if result.get('success'):
            return jsonify({
                "code": 200,
                "message": "预约成功",
                "data": {
                    "appointmentId": result.get('appointment_id'),
                    "sectionId": result.get('section_id')
                }
            })
        else:
            return jsonify({
                "code": 400,
                "message": result.get('message', '预约失败')
            })
    except Exception as e:
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})


@bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
def cancel_appointment(appointment_id):
    """取消预约"""
    patient_id = get_current_patient_id()
    if not patient_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        result = appointment_service.cancel_appointment(appointment_id)
        if result.get('success'):
            return jsonify({
                "code": 200,
                "message": "取消预约成功"
            })
        else:
            return jsonify({
                "code": 400,
                "message": result.get('message', '取消预约失败')
            })
    except Exception as e:
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})


@bp.route('/offices', methods=['GET'])
def get_all_offices():
    """获取所有科室信息"""
    patient_id = get_current_patient_id()
    if not patient_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        offices = office_repo.get_all_offices()
        offices_data = []

        for office in offices:
            offices_data.append({
                "officeID": office.officeID,
                "name": office.name,
                "description": getattr(office, 'description', '')
            })

        return jsonify({
            "code": 200,
            "message": "获取科室列表成功",
            "data": offices_data
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})


@bp.route('/doctors/by-office/<int:office_id>', methods=['GET'])
def get_doctors_by_office(office_id):
    """根据科室获取医生列表"""
    patient_id = get_current_patient_id()
    if not patient_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        doctors = appointment_service.get_doctors_by_office(office_id)
        doctors_data = []

        for doctor in doctors:
            doctors_data.append({
                "doctorID": doctor.doctorID,
                "doctor_name": doctor.doctor_name,
                "age": doctor.age,
                "office_name": doctor.office_name,
                "expertise_name": doctor.expertise_name,
                "position_name": doctor.position_name,
                "NumberOfPatients": doctor.NumberOfPatients
            })

        return jsonify({
            "code": 200,
            "message": "获取医生列表成功",
            "data": doctors_data
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})


@bp.route('/schedule/doctor', methods=['GET'])
def get_doctor_schedule():
    """获取医生排班信息"""
    patient_id = get_current_patient_id()
    if not patient_id:
        return jsonify({"code": 401, "message": "未认证"})

    doctor_id = request.args.get('doctorId', type=int)
    date_str = request.args.get('date')

    if not doctor_id or not date_str:
        return jsonify({"code": 400, "message": "缺少doctorId或date参数"})

    try:
        schedule = appointment_service.get_doctor_schedule_by_date(doctor_id, date_str)
        return safe_json_response({
            "code": 200,
            "message": "获取医生排班成功",
            "data": schedule
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})


@bp.route('/schedule/office', methods=['GET'])
def get_office_schedule():
    """获取科室排班信息"""
    patient_id = get_current_patient_id()
    if not patient_id:
        return jsonify({"code": 401, "message": "未认证"})

    office_id = request.args.get('officeId', type=int)
    date_str = request.args.get('date')

    if not office_id or not date_str:
        return jsonify({"code": 400, "message": "缺少officeId或date参数"})

    try:
        schedule = appointment_service.get_office_schedule_by_date(office_id, date_str)
        return safe_json_response({
            "code": 200,
            "message": "获取科室排班成功",
            "data": schedule
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})



@bp.route('/registration/appointment-availability/<int:section_id>', methods=['GET'])
def check_appointment_availability(section_id):
    """检查预约转挂号的可用性"""
    patient_id = get_current_patient_id()
    if not patient_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        result = registration_service.check_appointment_availability(section_id)
        return jsonify({
            "code": 200,
            "message": "获取预约可用性成功",
            "data": result
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})


@bp.route('/registration/register', methods=['POST'])
def register_patient():
    """患者挂号（支持直接挂号和预约转挂号）"""
    patient_id = get_current_patient_id()
    if not patient_id:
        return jsonify({"code": 401, "message": "未认证"})

    data = request.get_json()
    if not data:
        return jsonify({"code": 400, "message": "请求数据不能为空"})

    office_id = data.get('officeId')
    datetime_str = data.get('datetime')
    section_id = data.get('sectionId')

    try:
        if section_id:
            # 预约患者转挂号
            print(f"🔍 API层调试: 患者 {patient_id} 预约转挂号 section {section_id}")
            success = registration_service.register_with_appointment(patient_id, section_id)
            print(f"🔍 API层调试: register_with_appointment 返回 {success}")

            if success:
                # 获取挂号详情
                print(f"🔍 API调试: patient_id={patient_id}, section_id={section_id}")
                details = registration_service.get_registration_details(patient_id, section_id)
                print(f"🔍 API层调试: 获取挂号详情成功")
                return safe_json_response({
                    "code": 200,
                    "message": "挂号成功",
                    "data": details
                })
            else:
                print(f"🔍 API层调试: register_with_appointment 返回 False，挂号失败")
                return jsonify({"code": 400, "message": "挂号失败"})
        else:
            # 未预约患者直接挂号
            if not office_id or not datetime_str:
                return jsonify({"code": 400, "message": "缺少officeId或datetime参数"})

            success, new_section_id = registration_service.register_without_appointment(
                patient_id, office_id, datetime_str)
            if success:
                details = registration_service.get_registration_details(patient_id, new_section_id)
                return safe_json_response({
                    "code": 200,
                    "message": "挂号成功",
                    "data": details
                })
            else:
                return jsonify({"code": 400, "message": "挂号失败，可能没有可用名额"})
    except Exception as e:
        print(f"🔍 API层调试: 发生异常 {e}")
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})


@bp.route('/registration/history', methods=['GET'])
def get_registration_history():
    """获取患者挂号历史"""
    patient_id = get_current_patient_id()
    if not patient_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        registrations = registration_service.get_patient_registrations(patient_id)
        return safe_json_response({
            "code": 200,
            "message": "获取挂号历史成功",
            "data": registrations
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})


@bp.route('/registration/details', methods=['GET'])
def get_registration_details():
    """获取挂号详情"""
    patient_id = get_current_patient_id()
    if not patient_id:
        return jsonify({"code": 401, "message": "未认证"})

    section_id = request.args.get('sectionId', type=int)
    if not section_id:
        return jsonify({"code": 400, "message": "缺少sectionId参数"})

    try:
        details = registration_service.get_registration_details(patient_id, section_id)
        if "error" in details:
            return jsonify({"code": 400, "message": details["error"]})

        return safe_json_response({
            "code": 200,
            "message": "获取挂号详情成功",
            "data": details
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})


@bp.route('/profile', methods=['GET'])
def get_patient_profile():
    """获取患者个人信息"""
    patient_id = get_current_patient_id()
    if not patient_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        patient = patient_repo.get_patient_by_id(patient_id)
        if not patient:
            return jsonify({"code": 404, "message": "患者信息不存在"})

        patient_data = {
            "patientID": patient.patientsID,
            "name": patient.name,
            "age": patient.age,
        }

        return jsonify({
            "code": 200,
            "message": "获取患者信息成功",
            "data": patient_data
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})


@bp.route('/reports', methods=['GET'])
def get_reports():
    """获取检查报告"""
    patient_id = get_current_patient_id()
    if not patient_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        # 暂时返回空数据，后续实现具体逻辑
        return jsonify({
            "code": 200,
            "message": "获取报告成功",
            "data": []
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})


@bp.route('/reminders', methods=['GET'])
def get_reminders():
    """获取健康提醒"""
    patient_id = get_current_patient_id()
    if not patient_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        # 获取有效预约作为提醒
        result = appointment_service.get_patient_appointments(patient_id)
        reminders = []

        if result.get('success'):
            for appt in result.get('appointments', []):
                if appt.get('state') == 1:  # 有效预约
                    reminders.append({
                        "id": appt.get('appointmentID'),
                        "type": "预约提醒",
                        "content": f"您有一个预约：{appt.get('office_name', '')} - {appt.get('doctor_name', '')}",
                        "time": f"{appt.get('date', '')} {appt.get('starttime', '')}",
                        "status": "待就诊"
                    })

        return jsonify({
            "code": 200,
            "message": "获取提醒成功",
            "data": reminders
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})


@bp.route('/medical-records', methods=['GET'])
def get_medical_records():
    """获取患者完整病历记录"""
    patient_id = get_current_patient_id()
    if not patient_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        records = medical_record_service.get_patient_medical_records(patient_id)

        if records:
            # 格式化病历记录数据
            formatted_records = []
            for record in records:
                formatted_record = {
                    "registrationId": record.get('registrationID'),
                    "time": record.get('time'),
                    "information": record.get('information'),
                    "haveMedicine": record.get('have_medicine', False),
                    "doctor": {
                        "doctorId": record['doctor'].doctorID if record.get('doctor') else None,
                        "doctorName": record['doctor'].doctor_name if record.get('doctor') else None,
                        "officeName": record['doctor'].office_name if record.get('doctor') else None,
                        "expertiseName": record['doctor'].expertise_name if record.get('doctor') else None,
                        "positionName": record['doctor'].position_name if record.get('doctor') else None
                    } if record.get('doctor') else None
                }

                # 添加处方信息
                if record.get('have_medicine') and record.get('prescription'):
                    formatted_record["prescription"] = []
                    for item in record['prescription']:
                        medicine = item.get('medicine')
                        order = item.get('order')
                        if medicine and order:
                            formatted_record["prescription"].append({
                                "medicineId": medicine.medicineID,
                                "medicineName": medicine.name,
                                "price": medicine.price,
                                "amount": order.amount,
                                "totalPrice": order.price,
                                "description": medicine.description
                            })

                formatted_records.append(formatted_record)

            return jsonify({
                "code": 200,
                "message": "获取病历记录成功",
                "data": formatted_records
            })
        else:
            return jsonify({
                "code": 200,
                "message": "暂无病历记录",
                "data": []
            })

    except Exception as e:
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})



@bp.route('/medical-records/<int:registration_id>/prescription', methods=['GET'])
def get_prescription_details(registration_id):
    """获取特定病历的处方详情"""
    patient_id = get_current_patient_id()
    if not patient_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        prescription = medical_record_service.get_prescription_details(registration_id)

        if prescription:
            formatted_prescription = []
            total_price = 0

            for item in prescription:
                medicine = item.get('medicine')
                order = item.get('order')
                if medicine and order:
                    total_price += order.price
                    formatted_prescription.append({
                        "medicineId": medicine.medicineID,
                        "medicineName": medicine.name,
                        "unitPrice": medicine.price,
                        "amount": order.amount,
                        "totalPrice": order.price,
                        "description": medicine.description
                    })

            return jsonify({
                "code": 200,
                "message": "获取处方详情成功",
                "data": {
                    "registrationId": registration_id,
                    "medicines": formatted_prescription,
                    "totalPrice": total_price,
                    "medicineCount": len(formatted_prescription)
                }
            })
        else:
            return jsonify({
                "code": 200,
                "message": "该病历无处方信息",
                "data": {
                    "registrationId": registration_id,
                    "medicines": [],
                    "totalPrice": 0,
                    "medicineCount": 0
                }
            })

    except Exception as e:
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})


@bp.route('/health-overview', methods=['GET'])
def get_health_overview():
    """获取患者健康概览（综合信息，用于首页展示）"""
    patient_id = get_current_patient_id()
    if not patient_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        # 获取病历摘要
        medical_summary = medical_record_service.get_medical_record_summary(patient_id)

        # 获取预约信息
        appointment_result = appointment_service.get_patient_appointments(patient_id)

        appointments = []
        if appointment_result and appointment_result.get('success'):
            appointments = appointment_result.get('appointments', [])
        else:
            print(f"🔍 健康概览调试: 预约服务返回异常: {appointment_result}")

        # 获取挂号历史
        registrations = []
        try:
            registrations = registration_service.get_patient_registrations(patient_id)
        except Exception as e:
            registrations = []

        # 构建健康概览 - 确保所有字段都有默认值
        total_records = medical_summary.get('total_records', 0) if medical_summary else 0
        records_with_medicine = medical_summary.get('records_with_medicine', 0) if medical_summary else 0

        overview = {
            "patientId": patient_id,
            "statistics": {
                "medicalRecords": total_records,
                "upcomingAppointments": len([a for a in appointments if a and a.get('state') == 1]),
                "totalRegistrations": len(registrations) if registrations else 0,
                "prescriptionRate": round((records_with_medicine / total_records * 100), 1) if total_records > 0 else 0
            },
            "recentInfo": {
                "lastDoctor": medical_summary.get('recent_doctor') if medical_summary else None,
                "lastVisit": medical_summary.get('recent_record_time') if medical_summary else None
            },
            "lastUpdate": datetime.now().isoformat()
        }

        return jsonify({
            "code": 200,
            "message": "获取健康概览成功",
            "data": overview
        })

    except Exception as e:
        print(f"🔍 健康概览调试: 发生异常: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})

@bp.route('/test/connection', methods=['GET'])
def test_connection():
    """测试连接接口"""
    return jsonify({
        "code": 200,
        "message": "患者API连接正常",
        "timestamp": datetime.now().isoformat()
    })