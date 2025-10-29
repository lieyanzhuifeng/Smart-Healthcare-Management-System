# api/doctor.py
import sys
import os
# 添加这一行 - 告诉Python去上一级目录找模块
sys.path.append('..')
from flask import Blueprint, request, jsonify
from services.AuthService import AuthService
from repository.registration import RegistrationRepository
from repository.doctor import DoctorRepository

bp = Blueprint('doctor', __name__)
auth_service = AuthService()
registration_repo = RegistrationRepository()
doctor_repo = DoctorRepository()


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
        # 获取医生今日的挂号患者
        today_patients = registration_repo.get_today_patients_by_doctor(doctor_id)

        patients_data = []
        for patient in today_patients:
            patients_data.append({
                "id": patient.get('patientsID'),
                "name": patient.get('patient_name'),
                "age": patient.get('age'),
                "gender": "未知",  # 根据你的模型调整
                "time": patient.get('appointment_time'),
                "complaint": patient.get('complaint', '暂无主诉'),
                "status": map_registration_status(patient.get('state'))
            })

        return jsonify({
            "code": 200,
            "data": patients_data
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})


@bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取医生统计数据"""
    doctor_id = get_current_doctor_id()
    if not doctor_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        # 获取统计数据
        stats = registration_repo.get_doctor_statistics(doctor_id)

        return jsonify({
            "code": 200,
            "data": {
                "todayPatients": stats.get('today_patients', 0),
                "pendingPatients": stats.get('pending_patients', 0),
                "pendingRecords": stats.get('pending_records', 0),
                "consultRequests": stats.get('consult_requests', 0)
            }
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"系统错误: {str(e)}"})


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


@bp.route('/prescriptions', methods=['POST'])
def create_prescription():
    """创建电子处方"""
    doctor_id = get_current_doctor_id()
    if not doctor_id:
        return jsonify({"code": 401, "message": "未认证"})

    data = request.get_json()
    # 处方创建逻辑

    return jsonify({
        "code": 200,
        "message": "处方创建成功",
        "data": {"prescriptionId": 1}
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