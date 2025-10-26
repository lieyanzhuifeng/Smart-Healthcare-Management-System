import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from repository.base import Base
from typing import List, Optional
from model import Office, Doctor


class OfficeRepository(Base):
    def get_all_offices(self) -> List[Office]:
        """获取所有科室"""
        try:
            query = "SELECT officeID, name FROM office"
            results = self.execute_query(query)
            # 将查询结果转换为Office对象列表
            return [Office.from_dict(row) for row in results]
        except Exception as e:
            print(f"❌ 获取所有科室失败: {e}")
            return []

    def get_office_by_id(self, office_id: int) -> Optional[Office]:
        """根据科室ID获取科室信息"""
        try:
            query = "SELECT officeID, name FROM office WHERE officeID = %s"
            results = self.execute_query(query, (office_id,))

            if results and len(results) > 0:
                return Office.from_dict(results[0])
            else:
                print(f"⚠️ 未找到科室ID为 {office_id} 的科室")
                return None
        except Exception as e:
            print(f"❌ 根据ID获取科室失败 (ID: {office_id}): {e}")
            return None

    def get_offices_by_ids(self, office_ids: List[int]) -> List[Office]:
        """根据科室ID列表批量获取科室信息"""
        try:
            if not office_ids:
                return []

            # 构建IN查询的占位符
            placeholders = ', '.join(['%s'] * len(office_ids))
            query = f"SELECT officeID, name FROM office WHERE officeID IN ({placeholders})"
            results = self.execute_query(query, tuple(office_ids))

            return [Office.from_dict(row) for row in results]
        except Exception as e:
            print(f"❌ 批量获取科室失败: {e}")
            return []

    def get_office_by_name(self, name: str) -> Optional[Office]:
        """根据科室名称获取科室信息"""
        try:
            query = "SELECT officeID, name FROM office WHERE name = %s"
            results = self.execute_query(query, (name,))

            if results and len(results) > 0:
                return Office.from_dict(results[0])
            else:
                print(f"⚠️ 未找到名称为 '{name}' 的科室")
                return None
        except Exception as e:
            print(f"❌ 根据名称获取科室失败 (名称: {name}): {e}")
            return None

    def search_offices_by_keyword(self, keyword: str) -> List[Office]:
        """根据关键词搜索科室"""
        try:
            query = "SELECT officeID, name FROM office WHERE name LIKE %s"
            results = self.execute_query(query, (f'%{keyword}%',))

            return [Office.from_dict(row) for row in results]
        except Exception as e:
            print(f"❌ 搜索科室失败 (关键词: {keyword}): {e}")
            return []