# api/pharmacy.py
import sys
import os

# 添加这一行 - 告诉Python去上一级目录找模块
sys.path.append('..')
from flask import Blueprint, request, jsonify
from services.AuthService import AuthService
from services.PharmacyService import PharmacyService

bp = Blueprint('pharmacy', __name__)
auth_service = AuthService()
pharmacy_service = PharmacyService()


def get_current_pharmacy_id():
    """从token获取当前药房人员ID"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None
    user_info = auth_service.verify_token(token)
    return user_info.get('user_id') if user_info and user_info.get('role') == 'pharmacy' else None


@bp.route('/medicines', methods=['GET'])
def get_all_medicines():
    """获取所有药品及库存信息"""
    pharmacy_id = get_current_pharmacy_id()
    if not pharmacy_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        medicines = pharmacy_service.get_all_medicines_with_stock()
        return jsonify({
            "code": 200,
            "message": "获取成功",
            "data": medicines
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"})


@bp.route('/prescriptions', methods=['GET'])
def get_prescriptions():
    """获取处方列表（支持按状态筛选）"""
    pharmacy_id = get_current_pharmacy_id()
    if not pharmacy_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        # 获取查询参数
        state = request.args.get('state', type=int)

        if state is None:
            # 如果没有指定状态，默认返回待配药处方（状态2）
            state = 2

        if state not in [2, 3, 4]:
            return jsonify({"code": 400, "message": "状态参数错误，必须是2、3或4"})

        prescriptions = pharmacy_service.get_prescriptions_by_state(state)

        # 状态映射
        status_map = {
            2: "待配药",
            3: "已配药",
            4: "已取药"
        }

        return jsonify({
            "code": 200,
            "message": "获取成功",
            "data": {
                "status": status_map.get(state, "未知"),
                "statusCode": state,
                "prescriptions": prescriptions
            }
        })

    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"})


@bp.route('/prescriptions/pending', methods=['GET'])
def get_pending_prescriptions():
    """获取待配药处方（状态2）"""
    pharmacy_id = get_current_pharmacy_id()
    if not pharmacy_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        prescriptions = pharmacy_service.get_prescriptions_by_state(2)
        return jsonify({
            "code": 200,
            "message": "获取成功",
            "data": prescriptions
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"})


@bp.route('/prescriptions/ready', methods=['GET'])
def get_ready_prescriptions():
    """获取已配药处方（状态3）"""
    pharmacy_id = get_current_pharmacy_id()
    if not pharmacy_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        prescriptions = pharmacy_service.get_prescriptions_by_state(3)
        return jsonify({
            "code": 200,
            "message": "获取成功",
            "data": prescriptions
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"})


@bp.route('/prescriptions/completed', methods=['GET'])
def get_completed_prescriptions():
    """获取已取药处方（状态4）"""
    pharmacy_id = get_current_pharmacy_id()
    if not pharmacy_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        prescriptions = pharmacy_service.get_prescriptions_by_state(4)
        return jsonify({
            "code": 200,
            "message": "获取成功",
            "data": prescriptions
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"})


@bp.route('/prescriptions/<int:registration_id>/dispense', methods=['POST'])
def dispense_prescription(registration_id):
    """配药操作"""
    pharmacy_id = get_current_pharmacy_id()
    if not pharmacy_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        result = pharmacy_service.dispense_medicine(registration_id)

        if result['success']:
            return jsonify({
                "code": 200,
                "message": "配药成功",
                "data": {
                    "registrationId": result['registration_id'],
                    "medicineList": result.get('medicine_list', ''),
                    "totalPrice": result.get('total_price', 0),
                    "dispensedMedicines": result.get('dispensed_medicines', [])
                }
            })
        else:
            return jsonify({
                "code": 400,
                "message": result['message'],
                "data": {
                    "insufficientMedicines": result.get('insufficient_medicines', [])
                }
            })

    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"})


@bp.route('/prescriptions/<int:registration_id>/take', methods=['POST'])
def take_medicine(registration_id):
    """取药操作"""
    pharmacy_id = get_current_pharmacy_id()
    if not pharmacy_id:
        return jsonify({"code": 401, "message": "未认证"})

    try:
        result = pharmacy_service.take_medicine(registration_id)

        if result['success']:
            return jsonify({
                "code": 200,
                "message": "取药成功",
                "data": {
                    "registrationId": result['registration_id'],
                    "medicineList": result.get('medicine_list', ''),
                    "totalPrice": result.get('total_price', 0)
                }
            })
        else:
            return jsonify({
                "code": 400,
                "message": result['message']
            })

    except Exception as e:
        return jsonify({"code": 500, "message": f"服务器错误: {str(e)}"})

