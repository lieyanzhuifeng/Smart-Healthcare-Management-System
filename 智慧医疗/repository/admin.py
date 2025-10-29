# repository/admin.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import Admin
from repository.base import Base

class AdminRepository(Base):
    def get_admin_by_id(self, admin_id: int):
        """根据ID获取管理员"""
        query = "SELECT * FROM admin WHERE adminID = %s"
        result = self.execute_query(query, (admin_id,))
        return Admin.from_dict(result[0]) if result else None