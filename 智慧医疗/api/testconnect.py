# test_db_simple.py
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_database():
    print("测试数据库连接池...")

    try:
        # 直接导入base，触发连接池初始化
        from repository.base import Base
        print("✅ 数据库连接池初始化成功！")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


if __name__ == "__main__":
    test_database()