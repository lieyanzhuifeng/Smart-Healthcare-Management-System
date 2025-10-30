import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jwt
import datetime
import hashlib
import secrets
import time
from repository.account import AccountRepository


class AuthService:
    # 类属性 - 所有实例共享
    _active_tokens = {}

    def __init__(self):
        # 直接创建AccountRepository实例，它内部会处理数据库连接
        self.account_repo = AccountRepository()
        self.secret_key = "2353596wuruize2353579sunxiuming_dingzhenyao_mhy"

        # 存储挑战码（生产环境建议用Redis）
        self.challenges = {}
        # 固定盐值用于密码哈希
        self.password_salt = "medical_system_salt_2024"

    def login(self, username, password, role):
        try:
            user_id = int(username)

            # 使用AccountRepository获取用户
            user = self.account_repo.get_user_by_username(username, role)
            if not user:
                return {"code": 401, "message": "用户不存在"}

            # 验证密码
            if not self.verify_password(password, getattr(user, 'password_hash', None)):
                return {"code": 401, "message": "密码错误"}

            token = self.generate_token(user_id, role)

            # 构建用户信息
            user_info = self.build_user_info(user, role)

            return {
                "code": 200,
                "message": "登录成功",
                "data": {
                    "token": token,
                    "user": user_info
                }
            }
        except ValueError:
            return {"code": 400, "message": "用户名格式错误"}
        except Exception as e:
            return {"code": 500, "message": f"登录失败: {str(e)}"}

    # 密码哈希相关方法
    def hash_password(self, password: str) -> str:
        """使用SHA-256哈希密码"""
        password_with_salt = password + self.password_salt
        return hashlib.sha256(password_with_salt.encode()).hexdigest()

    def verify_password(self, input_password, stored_hash):
        """验证密码"""
        # 如果数据库密码为NULL，任何密码都算对（兼容旧数据）
        if stored_hash is None or stored_hash == "NULL" or stored_hash == "":
            return True

        # 验证哈希密码
        input_hash = self.hash_password(input_password)
        return input_hash == stored_hash

    # 挑战-响应机制
    def generate_challenge(self, username: str, role: str) -> dict:
        """生成挑战码"""
        try:
            challenge = secrets.token_hex(32)
            expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)

            # 存储挑战码
            challenge_key = f"{role}:{username}"
            self.challenges[challenge_key] = {
                "challenge": challenge,
                "expires_at": expires_at,
                "attempts": 0  # 尝试次数
            }

            return {
                "code": 200,
                "message": "挑战码生成成功",
                "data": {
                    "challenge": challenge,
                    "expires_in": 300  # 5分钟
                }
            }
        except Exception as e:
            return {"code": 500, "message": f"生成挑战码失败: {str(e)}"}

    def login_with_challenge(self, username: str, role: str, challenge: str, response: str) -> dict:
        """使用挑战-响应机制登录"""
        try:
            user_id = int(username)
            challenge_key = f"{role}:{username}"

            # 获取挑战数据
            challenge_data = self.challenges.get(challenge_key)
            if not challenge_data:
                return {"code": 401, "message": "挑战码不存在或已过期"}

            # 检查挑战码是否过期
            if datetime.datetime.utcnow() > challenge_data["expires_at"]:
                del self.challenges[challenge_key]
                return {"code": 401, "message": "挑战码已过期"}

            # 检查尝试次数
            if challenge_data["attempts"] >= 3:
                del self.challenges[challenge_key]
                return {"code": 401, "message": "尝试次数过多"}

            # 验证挑战码
            if challenge_data["challenge"] != challenge:
                challenge_data["attempts"] += 1
                return {"code": 401, "message": "挑战码不匹配"}

            # 获取用户
            user = self.account_repo.get_user_by_username(username, role)
            if not user:
                return {"code": 401, "message": "用户不存在"}

            # 验证响应（响应应该是挑战码+密码哈希的哈希）
            expected_response = self._calculate_expected_response(
                challenge,
                getattr(user, 'password_hash', '')
            )

            if response != expected_response:
                challenge_data["attempts"] += 1
                return {"code": 401, "message": "响应验证失败"}

            # 登录成功，清理挑战码
            del self.challenges[challenge_key]

            # 生成token
            token = self.generate_token(user_id, role)
            user_info = self.build_user_info(user, role)

            return {
                "code": 200,
                "message": "登录成功",
                "data": {
                    "token": token,
                    "user": user_info
                }
            }

        except ValueError:
            return {"code": 400, "message": "用户名格式错误"}
        except Exception as e:
            return {"code": 500, "message": f"挑战响应登录失败: {str(e)}"}

    def _calculate_expected_response(self, challenge: str, password_hash: str) -> str:
        """计算期望的响应值"""
        # 响应 = SHA256(挑战码 + 密码哈希)
        response_data = challenge + (password_hash or "")
        return hashlib.sha256(response_data.encode()).hexdigest()

    # 密码修改功能
    def change_password(self, token: str, old_password: str, new_password: str) -> dict:
        """修改密码"""
        try:
            # 验证token
            payload = self.verify_token(token)
            if not payload:
                return {"code": 401, "message": "无效的token"}

            user_id = payload['user_id']
            role = payload['role']

            # 获取用户
            user = self.account_repo.get_user_by_username(str(user_id), role)
            if not user:
                return {"code": 401, "message": "用户不存在"}

            # 验证旧密码
            if not self.verify_password(old_password, getattr(user, 'password_hash', None)):
                return {"code": 401, "message": "旧密码错误"}

            # 更新密码
            new_password_hash = self.hash_password(new_password)
            update_result = self.account_repo.update_password(user_id, role, new_password_hash)

            if update_result["success"]:
                return {"code": 200, "message": "密码修改成功"}
            else:
                return {"code": 500, "message": update_result["message"]}

        except Exception as e:
            return {"code": 500, "message": f"密码修改失败: {str(e)}"}

    # 账户管理功能
    def create_account(self, user_data: dict, role: str) -> dict:
        """创建账户"""
        try:
            # 如果有密码，先进行哈希
            if 'password' in user_data:
                user_data['password_hash'] = self.hash_password(user_data['password'])
                del user_data['password']  # 移除明文密码

            result = self.account_repo.create_account(user_data, role)

            if result["success"]:
                return {
                    "code": 200,
                    "message": result["message"],
                    "data": {
                        "user_id": result["user_id"],
                        "role": result["role"]
                    }
                }
            else:
                return {"code": 500, "message": result["message"]}

        except Exception as e:
            return {"code": 500, "message": f"创建账户失败: {str(e)}"}

    def update_account_info(self, token: str, update_data: dict) -> dict:
        """更新账户信息"""
        try:
            # 验证token
            payload = self.verify_token(token)
            if not payload:
                return {"code": 401, "message": "无效的token"}

            user_id = payload['user_id']
            role = payload['role']

            result = self.account_repo.update_account_info(user_id, role, update_data)

            if result["success"]:
                return {"code": 200, "message": result["message"]}
            else:
                return {"code": 500, "message": result["message"]}

        except Exception as e:
            return {"code": 500, "message": f"更新账户信息失败: {str(e)}"}

    def delete_account(self, token: str) -> dict:
        """删除账户"""
        try:
            # 验证token
            payload = self.verify_token(token)
            if not payload:
                return {"code": 401, "message": "无效的token"}

            user_id = payload['user_id']
            role = payload['role']

            result = self.account_repo.delete_account(user_id, role)

            if result["success"]:
                return {"code": 200, "message": result["message"]}
            else:
                return {"code": 500, "message": result["message"]}

        except Exception as e:
            return {"code": 500, "message": f"删除账户失败: {str(e)}"}

    def get_account_info(self, token: str) -> dict:
        """获取账户信息"""
        try:
            # 验证token
            payload = self.verify_token(token)
            if not payload:
                return {"code": 401, "message": "无效的token"}

            user_id = payload['user_id']
            role = payload['role']

            result = self.account_repo.get_account_info(user_id, role)

            if result["success"]:
                return {
                    "code": 200,
                    "message": result["message"],
                    "data": result["data"]
                }
            else:
                return {"code": 500, "message": result["message"]}

        except Exception as e:
            return {"code": 500, "message": f"获取账户信息失败: {str(e)}"}

    # Token 相关方法 - 修改为使用类属性
    def verify_token(self, token):
        """验证token - 带调试信息"""
        print(f"=== Token验证调试 ===")
        print(f"收到的token: {token}")
        print(f"存储的token数量: {len(AuthService._active_tokens)}")

        # 清理过期token
        self.clean_expired_tokens()

        token_info = AuthService._active_tokens.get(token)
        if token_info:
            print(f"找到用户: {token_info}")
            return token_info
        else:
            print("token未找到")
            return None

    def get_profile_by_token(self, token):
        """获取用户信息"""
        token_info = self.verify_token(token)
        if not token_info:
            return {"code": 401, "message": "token无效"}

        user_id = token_info['user_id']
        role = token_info['role']

        result = self.account_repo.get_account_info(user_id, role)
        if result["success"]:
            return {"code": 200, "data": result["data"]}
        else:
            return {"code": 404, "message": result["message"]}

    def generate_token(self, user_id, role):
        """改进的token生成 - 有时效性"""
        import secrets
        import time
        import hashlib

        # 加入时间戳确保唯一性和时效性
        timestamp = int(time.time())
        expires_in = 24 * 3600  # 24小时

        token_data = f"{user_id}:{role}:{timestamp}:{expires_in}:{secrets.token_hex(16)}"
        token = hashlib.sha256(token_data.encode()).hexdigest()

        # 使用类属性存储
        AuthService._active_tokens[token] = {
            'user_id': user_id,
            'role': role,
            'created_at': timestamp,
            'expires_at': timestamp + expires_in
        }

        print(f"新token生成，当前总数: {len(AuthService._active_tokens)}")
        return token

    def clean_expired_tokens(self):
        """清理过期token"""
        current_time = time.time()
        expired_tokens = [
            token for token, info in AuthService._active_tokens.items()
            if current_time > info['expires_at']
        ]

        for token in expired_tokens:
            del AuthService._active_tokens[token]

        if expired_tokens:
            print(f"清理了 {len(expired_tokens)} 个过期token")

    def build_user_info(self, user, role):
        # 根据角色确定ID字段名
        if role == 'patient':
            user_id = user.patientsID
        elif role == 'doctor':
            user_id = user.doctorID
        elif role == 'pharmacy':
            user_id = user.pharmacymanID
        elif role == 'admin':
            user_id = user.adminID
        else:
            user_id = 0

        base_info = {
            "id": user_id,
            "name": user.name,
            "role": role
        }

        # 根据不同角色添加特有信息
        if role == 'patient':
            base_info["extInfo"] = {
                "age": user.age
            }
        elif role == 'doctor':
            base_info["extInfo"] = {
                "expertiseID": user.expertiseID,
                "officeID": user.officeID,
                "positionID": user.positionID
            }
        elif role == 'pharmacy':
            base_info["extInfo"] = {
                "age": user.age
            }
        elif role == 'admin':
            base_info["extInfo"] = {
                "age": user.age
            }

        return base_info