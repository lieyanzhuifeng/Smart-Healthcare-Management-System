import mysql.connector
from mysql.connector import Error, pooling
from typing import List, Optional, Type, TypeVar, Any, Dict, Union
from abc import ABC
import logging

T = TypeVar('T')

class Base:
    """医院管理系统基础数据操作类 - 集成所有表操作"""

    def __init__(self):
        self.connection_pool = None
        self._init_connection_pool()
        self.logger = logging.getLogger(__name__)

    def _init_connection_pool(self):
        """初始化数据库连接池"""
        try:
            self.connection_pool = pooling.MySQLConnectionPool(
                pool_name="hospital_pool",
                pool_size=5,
                host='47.100.240.111',
                database='hospital_management',
                user='root',
                password='Db123456',
                port=3306,
                charset='utf8mb4',
                autocommit=True
            )
            print("✅ 数据库连接池初始化成功!")
        except Error as e:
            print(f"❌ 连接池初始化错误: {e}")
            raise

    def get_connection(self):
        """从连接池获取连接"""
        try:
            return self.connection_pool.get_connection()  # 修正：应该是connection_pool
        except Error as e:
            self.logger.error(f"获取数据库连接错误: {e}")
            raise

    def execute_query(self, query: str, params: tuple = None) -> List[dict]:
        """执行查询语句"""
        connection = self.get_connection()
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except Error as e:
            self.logger.error(f"查询执行错误: {e} - Query: {query}")
            raise
        finally:
            connection.close()

    def execute_update(self, query: str, params: tuple = None) -> int:
        """执行更新操作，返回影响的行数"""
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                connection.commit()
                return cursor.rowcount
        except Error as e:
            self.logger.error(f"更新操作错误: {e} - Query: {query}")
            connection.rollback()
            raise
        finally:
            connection.close()

    def _dict_to_model(self, data: dict, model_class: Type[T]) -> T:
        """将字典转换为模型对象"""
        if hasattr(model_class, 'from_dict'):
            return model_class.from_dict(data)
        else:
            return model_class(**data)