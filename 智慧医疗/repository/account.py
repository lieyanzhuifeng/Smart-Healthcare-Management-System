import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repository.base import Base
from model import Patients, Doctor, PharmacyMan, Admin
from typing import Optional, Dict, Any


class AccountRepository(Base):
    """账户管理Repository，统一处理所有用户类型的账户操作"""

    def __init__(self):
        super().__init__()  # 初始化Base类，建立数据库连接

    def _get_table_by_role(self, role: str) -> str:
        """根据角色获取对应的表名"""
        tables = {
            'patient': 'patients',
            'doctor': 'doctor',
            'pharmacy': 'pharmacyman',
            'admin': 'admin'
        }
        return tables.get(role)

    def _get_id_field_by_role(self, role: str) -> str:
        """根据角色获取ID字段名"""
        id_fields = {
            'patient': 'patientsID',
            'doctor': 'doctorID',
            'pharmacy': 'pharmacymanID',
            'admin': 'adminID'
        }
        return id_fields.get(role)

    def create_account(self, user_data: dict, role: str) -> Dict[str, Any]:
        """创建账户"""
        try:
            # 根据角色分别处理
            if role == 'patient':
                return self._create_patient_account(user_data)
            elif role == 'doctor':
                return self._create_doctor_account(user_data)
            elif role == 'pharmacy':
                return self._create_pharmacy_account(user_data)
            elif role == 'admin':
                return self._create_admin_account(user_data)
            else:
                return {"success": False, "message": "无效的用户角色"}

        except Exception as e:
            return {"success": False, "message": f"创建账户失败: {str(e)}"}

    def _create_patient_account(self, user_data: dict) -> Dict[str, Any]:
        """创建患者账户"""
        connection = self.get_connection()
        try:
            # 处理密码哈希
            from services.AuthService import AuthService
            auth_service = AuthService()

            password_hash = ""
            if 'password' in user_data:
                password_hash = auth_service.hash_password(user_data['password'])

            # 构建插入数据
            insert_data = {
                'name': user_data.get('name', ''),
                'age': user_data.get('age', 0),
                'password_hash': password_hash
            }

            with connection.cursor() as cursor:
                # 执行插入
                query = "INSERT INTO patients (name, age, password_hash) VALUES (%s, %s, %s)"
                cursor.execute(query, (insert_data['name'], insert_data['age'], insert_data['password_hash']))

                # 在同一个连接中获取最后插入的ID
                cursor.execute("SELECT LAST_INSERT_ID() as last_id")
                result = cursor.fetchone()
                user_id = result[0] if result else 0

                connection.commit()

                print(f"📝 创建的patient账户ID: {user_id}")  # 调试信息

                return {
                    "success": True,
                    "message": "患者账户创建成功",
                    "user_id": user_id,
                    "role": "patient"
                }

        except Exception as e:
            connection.rollback()
            return {"success": False, "message": f"创建患者账户失败: {str(e)}"}
        finally:
            connection.close()

    def _create_doctor_account(self, user_data: dict) -> Dict[str, Any]:
        """创建医生账户"""
        connection = self.get_connection()
        try:
            # 处理密码哈希
            from services.AuthService import AuthService
            auth_service = AuthService()

            password_hash = ""
            if 'password' in user_data:
                password_hash = auth_service.hash_password(user_data['password'])

            # 构建插入数据
            insert_data = {
                'name': user_data.get('name', ''),
                'age': user_data.get('age', 0),
                'expertiseID': user_data.get('expertiseID', 0),
                'officeID': user_data.get('officeID', 0),
                'positionID': user_data.get('positionID', 0),
                'NumberOfPatients': user_data.get('NumberOfPatients', 0),
                'password_hash': password_hash
            }

            with connection.cursor() as cursor:
                query = """
                        INSERT INTO doctor (name, age, expertiseID, officeID, positionID, NumberOfPatients, \
                                            password_hash)
                        VALUES (%s, %s, %s, %s, %s, %s, %s) \
                        """
                cursor.execute(query, (
                    insert_data['name'], insert_data['age'], insert_data['expertiseID'],
                    insert_data['officeID'], insert_data['positionID'], insert_data['NumberOfPatients'],
                    insert_data['password_hash']
                ))

                # 在同一个连接中获取最后插入的ID
                cursor.execute("SELECT LAST_INSERT_ID() as last_id")
                result = cursor.fetchone()
                user_id = result[0] if result else 0

                connection.commit()

                print(f"📝 创建的doctor账户ID: {user_id}")  # 调试信息

                return {
                    "success": True,
                    "message": "医生账户创建成功",
                    "user_id": user_id,
                    "role": "doctor"
                }

        except Exception as e:
            connection.rollback()
            return {"success": False, "message": f"创建医生账户失败: {str(e)}"}
        finally:
            connection.close()

    def _create_pharmacy_account(self, user_data: dict) -> Dict[str, Any]:
        """创建药房人员账户"""
        connection = self.get_connection()
        try:
            # 处理密码哈希
            from services.AuthService import AuthService
            auth_service = AuthService()

            password_hash = ""
            if 'password' in user_data:
                password_hash = auth_service.hash_password(user_data['password'])

            # 构建插入数据
            insert_data = {
                'name': user_data.get('name', ''),
                'age': user_data.get('age', 0),
                'password_hash': password_hash
            }

            with connection.cursor() as cursor:
                query = "INSERT INTO pharmacyman (name, age, password_hash) VALUES (%s, %s, %s)"
                cursor.execute(query, (insert_data['name'], insert_data['age'], insert_data['password_hash']))

                # 在同一个连接中获取最后插入的ID
                cursor.execute("SELECT LAST_INSERT_ID() as last_id")
                result = cursor.fetchone()
                user_id = result[0] if result else 0

                connection.commit()

                print(f"📝 创建的pharmacy账户ID: {user_id}")  # 调试信息

                return {
                    "success": True,
                    "message": "药房人员账户创建成功",
                    "user_id": user_id,
                    "role": "pharmacy"
                }

        except Exception as e:
            connection.rollback()
            return {"success": False, "message": f"创建药房人员账户失败: {str(e)}"}
        finally:
            connection.close()

    def _create_admin_account(self, user_data: dict) -> Dict[str, Any]:
        """创建管理员账户"""
        connection = self.get_connection()
        try:
            # 处理密码哈希
            from services.AuthService import AuthService
            auth_service = AuthService()

            password_hash = ""
            if 'password' in user_data:
                password_hash = auth_service.hash_password(user_data['password'])

            # 构建插入数据
            insert_data = {
                'name': user_data.get('name', ''),
                'age': user_data.get('age', 0),
                'password_hash': password_hash
            }

            with connection.cursor() as cursor:
                query = "INSERT INTO admin (name, age, password_hash) VALUES (%s, %s, %s)"
                cursor.execute(query, (insert_data['name'], insert_data['age'], insert_data['password_hash']))

                # 在同一个连接中获取最后插入的ID
                cursor.execute("SELECT LAST_INSERT_ID() as last_id")
                result = cursor.fetchone()
                user_id = result[0] if result else 0

                connection.commit()

                print(f"📝 创建的admin账户ID: {user_id}")  # 调试信息

                return {
                    "success": True,
                    "message": "管理员账户创建成功",
                    "user_id": user_id,
                    "role": "admin"
                }

        except Exception as e:
            connection.rollback()
            return {"success": False, "message": f"创建管理员账户失败: {str(e)}"}
        finally:
            connection.close()

    def update_password(self, user_id: int, role: str, new_password_hash: str) -> Dict[str, Any]:
        """更新密码"""
        try:
            table_name = self._get_table_by_role(role)
            id_field = self._get_id_field_by_role(role)

            if not table_name or not id_field:
                return {"success": False, "message": "无效的用户角色"}

            query = f"UPDATE {table_name} SET password_hash = %s WHERE {id_field} = %s"
            row_count = self.execute_update(query, (new_password_hash, user_id))

            if row_count > 0:
                return {"success": True, "message": "密码更新成功"}
            else:
                return {"success": False, "message": "用户不存在或密码更新失败"}

        except Exception as e:
            return {"success": False, "message": f"密码更新失败: {str(e)}"}

    def delete_account(self, user_id: int, role: str) -> Dict[str, Any]:
        """删除账户"""
        try:
            table_name = self._get_table_by_role(role)
            id_field = self._get_id_field_by_role(role)

            if not table_name or not id_field:
                return {"success": False, "message": "无效的用户角色"}

            query = f"DELETE FROM {table_name} WHERE {id_field} = %s"
            row_count = self.execute_update(query, (user_id,))

            if row_count > 0:
                return {"success": True, "message": "账户删除成功"}
            else:
                return {"success": False, "message": "用户不存在"}

        except Exception as e:
            return {"success": False, "message": f"删除账户失败: {str(e)}"}

    def get_account_info(self, user_id: int, role: str) -> Dict[str, Any]:
        """获取账户信息"""
        try:
            table_name = self._get_table_by_role(role)
            id_field = self._get_id_field_by_role(role)

            if not table_name or not id_field:
                return {"success": False, "message": "无效的用户角色"}

            query = f"SELECT * FROM {table_name} WHERE {id_field} = %s"
            result = self.execute_query(query, (user_id,))

            if not result:
                return {"success": False, "message": "用户不存在"}

            user_data = result[0]

            # 构建返回信息（不包含密码）
            user_info = {
                "user_id": user_id,
                "role": role,
                "name": user_data.get('name')
            }

            # 添加角色特定信息
            if role == 'patient':
                user_info["age"] = user_data.get('age')
            elif role == 'doctor':
                user_info.update({
                    "age": user_data.get('age'),
                    "expertiseID": user_data.get('expertiseID'),
                    "officeID": user_data.get('officeID'),
                    "positionID": user_data.get('positionID'),
                    "NumberOfPatients": user_data.get('NumberOfPatients')
                })
            elif role == 'pharmacy':
                user_info["age"] = user_data.get('age')
            elif role == 'admin':
                user_info["age"] = user_data.get('age')

            return {
                "success": True,
                "message": "获取账户信息成功",
                "data": user_info
            }

        except Exception as e:
            return {"success": False, "message": f"获取账户信息失败: {str(e)}"}

    def update_account_info(self, user_id: int, role: str, update_data: dict) -> Dict[str, Any]:
        """更新账户信息"""
        try:
            table_name = self._get_table_by_role(role)
            id_field = self._get_id_field_by_role(role)

            if not table_name or not id_field:
                return {"success": False, "message": "无效的用户角色"}

            # 移除密码字段，密码更新使用专门的方法
            update_data.pop('password_hash', None)
            update_data.pop('password', None)

            if not update_data:
                return {"success": False, "message": "没有可更新的字段"}

            # 构建SET子句
            set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
            values = list(update_data.values())
            values.append(user_id)  # 添加WHERE条件的值

            query = f"UPDATE {table_name} SET {set_clause} WHERE {id_field} = %s"
            row_count = self.execute_update(query, tuple(values))

            if row_count > 0:
                return {"success": True, "message": "账户信息更新成功"}
            else:
                return {"success": False, "message": "用户不存在或信息未变更"}

        except Exception as e:
            return {"success": False, "message": f"更新账户信息失败: {str(e)}"}

    def get_user_by_username(self, username: str, role: str):
        """根据用户名获取用户（这里简化处理，使用ID作为用户名）"""
        try:
            user_id = int(username)
            table_name = self._get_table_by_role(role)
            id_field = self._get_id_field_by_role(role)

            if not table_name or not id_field:
                return None

            query = f"SELECT * FROM {table_name} WHERE {id_field} = %s"
            result = self.execute_query(query, (user_id,))

            if result:
                user_data = result[0]
                # 根据角色创建对应的模型对象
                if role == 'patient':
                    return Patients.from_dict(user_data)
                elif role == 'doctor':
                    return Doctor.from_dict(user_data)
                elif role == 'pharmacy':
                    return PharmacyMan.from_dict(user_data)
                elif role == 'admin':
                    return Admin.from_dict(user_data)

            return None

        except (ValueError, Exception):
            return None