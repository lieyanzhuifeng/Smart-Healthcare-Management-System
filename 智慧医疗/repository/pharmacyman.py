# repository/pharmacyman.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import PharmacyMan
from repository.base import Base

class PharmacyManRepository(Base):
    def get_pharmacyman_by_id(self, pharmacyman_id: int):
        """根据ID获取药房人员"""
        query = "SELECT * FROM pharmacyman WHERE pharmacymanID = %s"
        result = self.execute_query(query, (pharmacyman_id,))
        return PharmacyMan.from_dict(result[0]) if result else None