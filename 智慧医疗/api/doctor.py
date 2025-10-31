# api/doctor.py
import sys
import os

# 添加这一行 - 告诉Python去上一级目录找模块
sys.path.append('..')
from flask import Blueprint, request, jsonify
from services.AuthService import AuthService
from services.DoctorWorkService import DoctorWorkService

bp = Blueprint('doctor', __name__)
auth_service = AuthService()
doctor_work_service = DoctorWorkService()


def get_current_doctor_id():
    """从token获取当前医生ID"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None
    user_info = auth_service.verify_token(token)
    return user_info.get('user_id') if user_info and user_info.get('role') == 'doctor' else None


@bp.route('/patients/today', methods=['GET'])
def get_today_patients():
    """获取今日患者列表"""
    doctor_id = get_current_doctor_id()
    if not doctor_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        # 获取当前日期
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')

        # 使用DoctorWorkService获取今日排班
        registrations = doctor_work_service.get_doctor_daily_schedule(doctor_id, today)

        # 格式化返回数据
        patients_data = []
        for reg in registrations:
            patients_data.append({
                "registrationId": reg['registrationID'],
                "patientId": reg['patient_id'],
                "patientName": reg['patient_name'],
                "patientAge": reg['patient_age'],
                "status": map_registration_status(reg['state']),
                "statusCode": reg['state'],
                "appointmentTime": f"{reg['date']} {reg['starttime']}-{reg['endtime']}",
                "queueNumber": reg['number']
            })

        return jsonify({
            "code": 200,
            "message": "获取成功",
            "data": patients_data
        })

    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"})


@bp.route('/patients/<int:registration_id>/start-visit', methods=['POST'])
def start_patient_visit(registration_id):
    """开始患者就诊"""
    doctor_id = get_current_doctor_id()
    if not doctor_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        success = doctor_work_service.start_patient_visit(registration_id)
        if success:
            return jsonify({
                "code": 200,
                "message": "就诊开始成功"
            })
        else:
            return jsonify({
                "code": 400,
                "message": "就诊开始失败，请检查挂号状态"
            })
    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"})


@bp.route('/patients/<int:registration_id>/medical-record', methods=['POST'])
def create_medical_record(registration_id):
    """创建就诊记录"""
    doctor_id = get_current_doctor_id()
    if not doctor_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        data = request.get_json()
        if not data or 'information' not in data:
            return jsonify({"code": 400, "message": "缺少必要参数"})

        information = data['information']
        have_medicine = data.get('haveMedicine', False)

        success = doctor_work_service.create_patient_medical_record(
            registration_id, information, doctor_id, have_medicine
        )

        if success:
            return jsonify({
                "code": 200,
                "message": "就诊记录创建成功"
            })
        else:
            return jsonify({
                "code": 400,
                "message": "就诊记录创建失败"
            })
    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"})


@bp.route('/medicines', methods=['GET'])
def get_medicines():
    """获取所有药品信息"""
    doctor_id = get_current_doctor_id()
    if not doctor_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        medicines = doctor_work_service.get_medicines_for_prescription()
        return jsonify({
            "code": 200,
            "message": "获取成功",
            "data": medicines
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"})


@bp.route('/prescriptions', methods=['POST'])
def create_prescription():
    """创建电子处方"""
    doctor_id = get_current_doctor_id()
    if not doctor_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        data = request.get_json()
        if not data or 'registrationId' not in data or 'medicines' not in data:
            return jsonify({"code": 400, "message": "缺少必要参数"})

        registration_id = data['registrationId']
        medicine_orders = data['medicines']

        # 验证药品数据格式
        for medicine in medicine_orders:
            if 'medicineID' not in medicine or 'amount' not in medicine:
                return jsonify({"code": 400, "message": "药品数据格式错误"})

        success = doctor_work_service.prescribe_medicines(registration_id, medicine_orders)

        if success:
            return jsonify({
                "code": 200,
                "message": "处方创建成功",
                "data": {"prescriptionId": registration_id}
            })
        else:
            return jsonify({
                "code": 400,
                "message": "处方创建失败"
            })

    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"})


@bp.route('/ai-diagnose/<int:patient_id>', methods=['GET'])
def get_ai_diagnose(patient_id):
    """获取AI诊断建议"""
    doctor_id = get_current_doctor_id()
    if not doctor_id:
        return jsonify({"code": 401, "message": "未认证"})

    # 模拟AI诊断数据
    return jsonify({
        "code": 200,
        "data": {
            "possibleDiagnosis": "上呼吸道感染（置信度：85%）",
            "suggestedTests": "血常规、C反应蛋白",
            "medicationSuggestions": "阿莫西林胶囊、布洛芬缓释片",
            "notes": "注意休息，多饮水"
        }
    })


def map_registration_status(state):
    """映射挂号状态"""
    status_map = {
        0: "待就诊",
        1: "就诊中",
        2: "已开处方",
        3: "药品已准备",
        4: "已完成",
        5: "已取消"
    }
    return status_map.get(state, "未知状态")