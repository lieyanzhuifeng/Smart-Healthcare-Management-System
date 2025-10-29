# api/patient.py
import sys
import os
# 添加这一行 - 告诉Python去上一级目录找模块
sys.path.append('..')
from flask import Blueprint, request, jsonify
from services.AppointmentService import AppointmentService
from services.RegistrationService import RegistrationService
from services.AuthService import AuthService

bp = Blueprint('patient', __name__)
appointment_service = AppointmentService()
registration_service = RegistrationService()
auth_service = AuthService()


def get_current_patient_id():
    """从token获取当前患者ID"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None
    user_info = auth_service.verify_token(token)
    return user_info.get('user_id') if user_info and user_info.get('role') == 'patient' else None


@bp.route('/appointments', methods=['GET'])
def get_appointments():
    """获取患者预约列表"""
    patient_id = get_current_patient_id()
    if not patient_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        result = appointment_service.get_patient_appointments(patient_id)
        if result.get('success'):
            appointments = []
            for appt in result.get('appointments', []):
                appointments.append({
                    "id": appt.get('appointmentID'),
                    "date": appt.get('date', '').split(' ')[0] if appt.get('date') else '',
                    "time": appt.get('time', ''),
                    "department": appt.get('office_name', ''),
                    "doctor": appt.get('doctor_name', ''),
                    "status": map_appointment_status(appt.get('state'))
                })

            return jsonify({
                "code": 200,
                "data": appointments
            })
        else:
            return jsonify({"code": 500, "message": result.get('message', '获取预约失败')})
    except Exception as e:
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})


@bp.route('/appointments', methods=['POST'])
def create_appointment():
    """创建预约"""
    patient_id = get_current_patient_id()
    if not patient_id:
        return jsonify({"code": 401, "message": "未认证"})

    data = request.get_json()
    section_id = data.get('sectionId')

    if not section_id:
        return jsonify({"code": 400, "message": "缺少sectionId参数"})

    try:
        result = appointment_service.create_appointment(patient_id, section_id)
        if result.get('success'):
            return jsonify({
                "code": 200,
                "message": "预约成功",
                "data": {"appointmentId": result.get('section_id')}
            })
        else:
            return jsonify({"code": 400, "message": result.get('message', '预约失败')})
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
            return jsonify({"code": 200, "message": "取消成功"})
        else:
            return jsonify({"code": 400, "message": result.get('message', '取消失败')})
    except Exception as e:
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})


@bp.route('/reports', methods=['GET'])
def get_reports():
    """获取检查报告"""
    patient_id = get_current_patient_id()
    if not patient_id:
        return jsonify({"code": 401, "message": "未认证"})

    # 暂时返回空数据，后续实现
    return jsonify({
        "code": 200,
        "data": []
    })


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
                        "time": f"今天 {appt.get('time', '')}",
                        "content": f"您有一个预约：{appt.get('office_name', '')} - {appt.get('doctor_name', '')}",
                        "type": "预约"
                    })

        return jsonify({
            "code": 200,
            "data": reminders
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})


def map_appointment_status(state):
    """映射预约状态"""
    status_map = {
        1: "待就诊",
        2: "已完成",
        3: "已取消"
    }
    return status_map.get(state, "未知状态")