import mysql.connector
from mysql.connector import Error, pooling
from typing import List, Optional, Type, TypeVar, Any, Dict, Union
from abc import ABC
import logging
import sys
import os
from datetime import time, datetime
from model import Timeslot

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from repository.base import Base


class TimeslotRepository(Base):
    def get_timeslot_by_time(self, time_str: str) -> Optional[Timeslot]:
        """根据时间字符串获取对应的时间段"""
        try:
            if ':' in time_str:
                time_parts = time_str.split(':')
                if len(time_parts) == 2:
                    time_obj = time(int(time_parts[0]), int(time_parts[1]))
                elif len(time_parts) == 3:
                    time_obj = time(int(time_parts[0]), int(time_parts[1]), int(time_parts[2]))
                else:
                    return None
            else:
                time_obj = time(int(time_str), 0, 0)

            query = "SELECT * FROM timeslot WHERE TIME(%s) BETWEEN starttime AND endtime"
            results = self.execute_query(query, (time_obj,))

            return Timeslot(**results[0]) if results else None

        except Exception:
            return None

    def get_all_timeslots(self) -> List[Timeslot]:
        """获取所有时间段，按开始时间排序"""
        try:
            query = "SELECT * FROM timeslot ORDER BY starttime"
            results = self.execute_query(query)
            return [Timeslot(**data) for data in results] if results else []
        except Exception:
            return []

    def get_timeslot_by_id(self, timeslot_id: int) -> Optional[Timeslot]:
        """根据ID获取时间段"""
        try:
            query = "SELECT * FROM timeslot WHERE timeslotID = %s"
            results = self.execute_query(query, (timeslot_id,))
            return Timeslot(**results[0]) if results else None
        except Exception:
            return None

    def get_timeslots_by_time_range(self, start_time: str, end_time: str) -> List[Timeslot]:
        """根据时间范围获取时间段"""
        try:
            query = """
                    SELECT * FROM timeslot 
                    WHERE starttime >= TIME(%s) AND endtime <= TIME(%s)
                    ORDER BY starttime
                    """
            results = self.execute_query(query, (start_time, end_time))
            return [Timeslot(**data) for data in results] if results else []
        except Exception:
            return []