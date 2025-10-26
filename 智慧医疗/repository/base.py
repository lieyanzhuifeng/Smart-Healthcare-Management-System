import mysql.connector
from mysql.connector import Error, pooling
from typing import List, Optional, Type, TypeVar, Any, Dict, Union
from abc import ABC
import logging
from contextlib import contextmanager

T = TypeVar('T')


class Base:
    """医院管理系统基础数据操作类 - 支持事务管理"""

    _connection_pool = None  # 类变量，所有实例共享

    def __init__(self):
        self._current_connection = None
        self._transaction_depth = 0
        self.logger = logging.getLogger(__name__)
        self._init_connection_pool()

    def _init_connection_pool(self):
        """初始化数据库连接池 - 单例模式"""
        if Base._connection_pool is not None:
            return  # 连接池已初始化，直接返回

        try:
            Base._connection_pool = pooling.MySQLConnectionPool(
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
            # 如果已经在事务中，返回当前连接
            if self._current_connection and not self._current_connection.is_closed():
                return self._current_connection
            # 使用类变量 _connection_pool，不是实例变量 connection_pool
            return Base._connection_pool.get_connection()
        except Error as e:
            self.logger.error(f"获取数据库连接错误: {e}")
            raise

    def begin_transaction(self):
        """开始事务"""
        if self._transaction_depth == 0:
            self._current_connection = Base._connection_pool.get_connection()  # 使用类变量
            self._current_connection.autocommit = False
        self._transaction_depth += 1

    def commit_transaction(self):
        """提交事务"""
        if self._transaction_depth > 0:
            self._transaction_depth -= 1
            if self._transaction_depth == 0 and self._current_connection:
                self._current_connection.commit()
                self._current_connection.autocommit = True
                self._current_connection.close()
                self._current_connection = None

    def rollback_transaction(self):
        """回滚事务"""
        if self._transaction_depth > 0 and self._current_connection:
            self._current_connection.rollback()
            self._current_connection.autocommit = True
            self._current_connection.close()
            self._current_connection = None
            self._transaction_depth = 0

    @contextmanager
    def transaction(self):
        """事务上下文管理器"""
        self.begin_transaction()
        try:
            yield
            self.commit_transaction()
        except Exception:
            self.rollback_transaction()
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
            # 只有在非事务模式下才关闭连接
            if self._transaction_depth == 0:
                connection.close()

    def execute_update(self, query: str, params: tuple = None) -> int:
        """执行更新操作，返回影响的行数"""
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                # 在事务模式下不自动提交
                if self._transaction_depth == 0:
                    connection.commit()
                return cursor.rowcount
        except Error as e:
            self.logger.error(f"更新操作错误: {e} - Query: {query}")
            if self._transaction_depth == 0:
                connection.rollback()
            raise
        finally:
            # 只有在非事务模式下才关闭连接
            if self._transaction_depth == 0:
                connection.close()