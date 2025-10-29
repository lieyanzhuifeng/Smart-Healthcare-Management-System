# api/admin.py
import sys
import os

# 添加项目根目录到路径
sys.path.append('..')

from flask import Blueprint, request, jsonify
from services.DoctorScheduleService import DoctorScheduleService
from services.AuthService import AuthService

bp = Blueprint('admin', __name__)
schedule_service = DoctorScheduleService()
auth_service = AuthService()


def get_current_admin_id():
    """从token获取当前管理员ID"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None
    user_info = auth_service.verify_token(token)
    return user_info.get('user_id') if user_info and user_info.get('role') == 'admin' else None


@bp.route('/schedules/generate', methods=['POST'])
def generate_schedules():
    """生成医生排班（不保存到数据库）"""
    admin_id = get_current_admin_id()
    if not admin_id:
        return jsonify({"code": 401, "message": "未认证或权限不足"})

    data = request.get_json()
    start_date = data.get('startDate')
    end_date = data.get('endDate')
    timeslots = data.get('timeslots', [1, 2, 3, 4])  # 默认所有时间段

    if not all([start_date, end_date]):
        return jsonify({"code": 400, "message": "缺少必要参数: startDate, endDate"})

    try:
        schedules = schedule_service.generate_schedules(start_date, end_date, timeslots)

        return jsonify({
            "code": 200,
            "message": "排班生成成功",
            "data": {
                "total": len(schedules),
                "schedules": schedules
            }
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"生成排班失败: {str(e)}"})


@bp.route('/schedules/save', methods=['POST'])
def save_schedules():
    """保存排班到数据库"""
    admin_id = get_current_admin_id()
    if not admin_id:
        return jsonify({"code": 401, "message": "未认证或权限不足"})

    data = request.get_json()
    schedules = data.get('schedules', [])

    if not schedules:
        return jsonify({"code": 400, "message": "没有排班数据"})

    try:
        success = schedule_service.save_schedules_to_database(schedules)

        if success:
            return jsonify({
                "code": 200,
                "message": f"成功保存 {len(schedules)} 条排班记录",
                "data": {
                    "savedCount": len(schedules)
                }
            })
        else:
            return jsonify({"code": 500, "message": "保存排班失败"})
    except Exception as e:
        return jsonify({"code": 500, "message": f"保存排班失败: {str(e)}"})


@bp.route('/schedules/generate-and-save', methods=['POST'])
def generate_and_save_schedules():
    """一键生成并保存排班"""
    admin_id = get_current_admin_id()
    if not admin_id:
        return jsonify({"code": 401, "message": "未认证或权限不足"})

    data = request.get_json()
    start_date = data.get('startDate')
    end_date = data.get('endDate')
    timeslots = data.get('timeslots', [1, 2, 3, 4])

    if not all([start_date, end_date]):
        return jsonify({"code": 400, "message": "缺少必要参数: startDate, endDate"})

    try:
        success = schedule_service.generate_and_save_schedules(start_date, end_date, timeslots)

        if success:
            return jsonify({
                "code": 200,
                "message": "排班生成并保存成功"
            })
        else:
            return jsonify({"code": 500, "message": "排班生成或保存失败"})
    except Exception as e:
        return jsonify({"code": 500, "message": f"排班操作失败: {str(e)}"})


@bp.route('/schedules/clear', methods=['POST'])
def clear_schedules():
    """清除指定日期范围的排班"""
    admin_id = get_current_admin_id()
    if not admin_id:
        return jsonify({"code": 401, "message": "未认证或权限不足"})

    data = request.get_json()
    start_date = data.get('startDate')
    end_date = data.get('endDate')

    if not all([start_date, end_date]):
        return jsonify({"code": 400, "message": "缺少必要参数: startDate, endDate"})

    try:
        success = schedule_service.clear_schedules(start_date, end_date)

        if success:
            return jsonify({
                "code": 200,
                "message": "排班清除成功"
            })
        else:
            return jsonify({"code": 500, "message": "排班清除失败"})
    except Exception as e:
        return jsonify({"code": 500, "message": f"清除排班失败: {str(e)}"})


@bp.route('/schedules/preview', methods=['GET'])
def preview_schedules():
    """预览指定日期的排班"""
    admin_id = get_current_admin_id()
    if not admin_id:
        return jsonify({"code": 401, "message": "未认证或权限不足"})

    date = request.args.get('date')
    if not date:
        return jsonify({"code": 400, "message": "缺少日期参数"})

    try:
        # 使用 Service 层的方法
        schedules = schedule_service.get_schedules_preview(date)

        return jsonify({
            "code": 200,
            "data": {
                "date": date,
                "schedules": schedules  # 现在返回真实的排班数据
            }
        })
    except Exception as e:
        return jsonify({"code": 500, "message": f"获取排班预览失败: {str(e)}"})


@bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取管理统计数据"""
    admin_id = get_current_admin_id()
    if not admin_id:
        return jsonify({"code": 401, "message": "未认证或权限不足"})

    # 模拟统计数据
    return jsonify({
        "code": 200,
        "data": {
            "outpatientVolume": 1245,
            "revenue": 328000,
            "bedUsageRate": 85,
            "patientSatisfaction": 4.8
        }
    })


@bp.route('/statistics/outpatient-trend', methods=['GET'])
def get_outpatient_trend():
    """获取门诊量趋势数据"""
    admin_id = get_current_admin_id()
    if not admin_id:
        return jsonify({"code": 401, "message": "未认证或权限不足"})

    days = request.args.get('days', 7, type=int)

    # 模拟趋势数据
    return jsonify({
        "code": 200,
        "data": {
            "labels": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
            "values": [1120, 1320, 1245, 1450, 1380, 980, 760]
        }
    })


@bp.route('/statistics/department-distribution', methods=['GET'])
def get_department_distribution():
    """获取科室分布数据"""
    admin_id = get_current_admin_id()
    if not admin_id:
        return jsonify({"code": 401, "message": "未认证或权限不足"})

    # 模拟科室分布数据
    return jsonify({
        "code": 200,
        "data": [
            {"name": "内科", "value": 156},
            {"name": "外科", "value": 98},
            {"name": "儿科", "value": 87},
            {"name": "妇产科", "value": 76}
        ]
    })


@bp.route('/departments', methods=['GET'])
def get_departments():
    """获取科室列表"""
    admin_id = get_current_admin_id()
    if not admin_id:
        return jsonify({"code": 401, "message": "未认证或权限不足"})

    # 模拟科室数据
    departments = [
        {
            "id": 1,
            "name": "内科",
            "director": "张主任",
            "doctors": 15,
            "beds": 50,
            "occupancy": 85,
            "todayPatients": 156,
            "revenue": 125000
        }
    ]

    return jsonify({
        "code": 200,
        "data": departments
    })


@bp.route('/notifications', methods=['GET'])
def get_notifications():
    """获取系统通知"""
    admin_id = get_current_admin_id()
    if not admin_id:
        return jsonify({"code": 401, "message": "未认证或权限不足"})

    # 模拟通知数据
    notifications = [
        {
            "id": 1,
            "time": "2024-01-15 09:00",
            "title": "设备维护提醒",
            "content": "本周六进行系统维护，请提前安排工作"
        }
    ]

    return jsonify({
        "code": 200,
        "data": notifications
    })


@bp.route('/health', methods=['GET'])
def health_check():
    """管理员健康检查"""
    admin_id = get_current_admin_id()
    if not admin_id:
        return jsonify({"code": 401, "message": "未认证或权限不足"})

    return jsonify({
        "code": 200,
        "message": "管理员服务运行正常",
        "data": {
            "adminId": admin_id,
            "timestamp": "2024-01-15 10:00:00"
        }
    })