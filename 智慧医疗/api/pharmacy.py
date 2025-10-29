# api/pharmacy.py
import sys
import os
# 添加这一行 - 告诉Python去上一级目录找模块
sys.path.append('..')
from flask import Blueprint, request, jsonify
from services.AuthService import AuthService

bp = Blueprint('pharmacy', __name__)
auth_service = AuthService()


def get_current_pharmacy_id():
    """从token获取当前药房人员ID"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None
    user_info = auth_service.verify_token(token)
    return user_info.get('user_id') if user_info and user_info.get('role') == 'pharmacy' else None


@bp.route('/prescriptions', methods=['GET'])
def get_prescriptions():
    """获取待配药处方"""
    pharmacy_id = get_current_pharmacy_id()
    if not pharmacy_id:
        return jsonify({"code": 401, "message": "未认证"})

    filter_type = request.args.get('filter', 'all')

    # 模拟处方数据
    prescriptions = [
        {
            "id": "P2024001",
            "patientName": "张三",
            "doctorName": "李医生",
            "time": "2024-01-15 10:30",
            "priority": "普通",
            "medicines": "阿莫西林胶囊*1, 布洛芬缓释片*2"
        }
    ]

    return jsonify({
        "code": 200,
        "data": prescriptions
    })


@bp.route('/prescriptions/<prescription_id>/dispense', methods=['POST'])
def dispense_prescription(prescription_id):
    """配药操作"""
    pharmacy_id = get_current_pharmacy_id()
    if not pharmacy_id:
        return jsonify({"code": 401, "message": "未认证"})

    return jsonify({"code": 200, "message": "配药成功"})


@bp.route('/inventory/alerts', methods=['GET'])
def get_inventory_alerts():
    """获取库存预警"""
    pharmacy_id = get_current_pharmacy_id()
    if not pharmacy_id:
        return jsonify({"code": 401, "message": "未认证"})

    # 模拟库存预警数据
    alerts = [
        {
            "id": 1,
            "name": "阿莫西林胶囊",
            "spec": "0.25g*24粒",
            "stock": 15,
            "threshold": 20,
            "expiry": "2024-06-30",
            "alertType": "库存不足"
        }
    ]

    return jsonify({
        "code": 200,
        "data": alerts
    })


@bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取药房统计数据"""
    pharmacy_id = get_current_pharmacy_id()
    if not pharmacy_id:
        return jsonify({"code": 401, "message": "未认证"})

    return jsonify({
        "code": 200,
        "data": {
            "pendingPrescriptions": 45,
            "medicineTypes": 1258,
            "stockAlerts": 12,
            "expiringSoon": 5
        }
    })