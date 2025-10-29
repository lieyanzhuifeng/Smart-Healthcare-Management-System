# services/AuthService.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jwt
import datetime
from repository.patient import PatientRepository
from repository.doctor import DoctorRepository


class AuthService:
    def __init__(self):
        self.patient_repo = PatientRepository()
        self.doctor_repo = DoctorRepository()
        self.secret_key = "your-secret-key"

    def login(self, username, password, role):
        try:
            user_id = int(username)

            if role == 'patient':
                user = self.patient_repo.get_patient_by_id(user_id)
            elif role == 'doctor':
                user = self.doctor_repo.get_doctor_by_id(user_id)
            else:
                return {"code": 400, "message": "无效的角色"}

            if not user:
                return {"code": 401, "message": "用户不存在"}

            # 处理密码为NULL的情况 - 任何密码都算对
            if not self.verify_password(password, getattr(user, 'password_hash', None)):
                return {"code": 401, "message": "密码错误"}

            # 生成token
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

    def get_profile_by_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            user_id = payload['user_id']
            role = payload['role']

            if role == 'patient':
                user = self.patient_repo.get_patient_by_id(user_id)
                profile_data = {
                    "id": user.patientsID,
                    "name": user.name,
                    "role": role,
                    "age": user.age,
                    "avatar": None,
                    "phone": None
                }
            elif role == 'doctor':
                user = self.doctor_repo.get_doctor_by_id(user_id)
                profile_data = {
                    "id": user.doctorID,
                    "name": user.name,
                    "role": role,
                    "age": user.age,
                    "avatar": None,
                    "phone": None,
                    "expertiseID": user.expertiseID,
                    "officeID": user.officeID,
                    "positionID": user.positionID
                }
            else:
                return {"code": 400, "message": "无效的角色"}

            return {"code": 200, "data": profile_data}
        except jwt.ExpiredSignatureError:
            return {"code": 401, "message": "token已过期"}
        except jwt.InvalidTokenError:
            return {"code": 401, "message": "无效的token"}
        except Exception as e:
            return {"code": 500, "message": f"获取信息失败: {str(e)}"}

    def verify_token(self, token):
        """验证token并返回payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except:
            return None

    def verify_password(self, input_password, stored_hash):
        """验证密码 - 如果数据库密码为NULL，任何密码都算对"""
        if stored_hash is None or stored_hash == "NULL" or stored_hash == "":
            # 数据库密码为NULL，允许任何密码登录
            return True
        # 如果有真实密码，进行验证
        return input_password == stored_hash

    def generate_token(self, user_id, role):
        payload = {
            'user_id': user_id,
            'role': role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def build_user_info(self, user, role):
        base_info = {
            "id": user.patientsID if role == 'patient' else user.doctorID,
            "name": user.name,
            "role": role
        }

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

        return base_info