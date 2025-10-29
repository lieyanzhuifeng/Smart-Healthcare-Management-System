# api/auth.py
import sys
import os
# 添加这一行 - 告诉Python去上一级目录找模块
sys.path.append('..')

from flask import Blueprint, request, jsonify
from services.AuthService import AuthService

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