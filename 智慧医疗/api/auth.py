import sys
import os
# 添加这一行 - 告诉Python去上一级目录找模块
sys.path.append('..')

from flask import Blueprint, request, jsonify
from services.AuthService import AuthService

# 这里定义的是 bp，不是 auth_bp
bp = Blueprint('auth', __name__)
auth_service = AuthService()

@bp.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    result = auth_service.login(username, password, role)
    return jsonify(result)

@bp.route('/logout', methods=['POST'])
def logout():
    """退出登录"""
    return jsonify({"code": 200, "message": "退出成功"})

@bp.route('/profile', methods=['GET'])
def get_profile():
    """获取个人信息"""
    # 从请求头获取token信息（简化版）
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({"code": 401, "message": "未认证"})

    result = auth_service.get_profile_by_token(token)
    return jsonify(result)

# 修正：这里应该使用 bp，不是 auth_bp
@bp.route('/challenge', methods=['POST'])
def generate_challenge():
    """生成挑战码"""
    data = request.get_json()
    username = data.get('username')
    role = data.get('role')

    auth_service = AuthService()
    result = auth_service.generate_challenge(username, role)
    return jsonify(result)

# 修正：这里应该使用 bp，不是 auth_bp
@bp.route('/login/challenge', methods=['POST'])
def login_with_challenge():
    """挑战-响应登录"""
    data = request.get_json()
    username = data.get('username')
    role = data.get('role')
    challenge = data.get('challenge')
    response = data.get('response')

    auth_service = AuthService()
    result = auth_service.login_with_challenge(username, role, challenge, response)
    return jsonify(result)

@bp.route('/change-password', methods=['POST'])
def change_password():
    """修改密码"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    auth_service = AuthService()
    result = auth_service.change_password(token, old_password, new_password)
    return jsonify(result)


# 账户管理路由
@bp.route('/account/create', methods=['POST'])
def create_account():
    """创建账户"""
    data = request.get_json()
    role = data.get('role')

    auth_service = AuthService()
    result = auth_service.create_account(data, role)
    return jsonify(result)


@bp.route('/account/update', methods=['POST'])
def update_account():
    """更新账户信息"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    data = request.get_json()

    auth_service = AuthService()
    result = auth_service.update_account_info(token, data)
    return jsonify(result)


@bp.route('/account/delete', methods=['POST'])
def delete_account():
    """删除账户"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    auth_service = AuthService()
    result = auth_service.delete_account(token)
    return jsonify(result)


@bp.route('/account/info', methods=['GET'])
def get_account_info():
    """获取账户信息"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    auth_service = AuthService()
    result = auth_service.get_account_info(token)
    return jsonify(result)