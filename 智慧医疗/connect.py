import mysql.connector
from mysql.connector import Error


def check_database_tables():
    """检查数据库中的所有表"""
    try:
        # 连接数据库
        connection = mysql.connector.connect(
            host='47.100.240.111',
            database='hospital_management',
            user='root',
            password='Db123456',
            port=3306
        )

        if connection.is_connected():
            print("✅ 成功连接到医院管理系统数据库!")

            cursor = connection.cursor()

            # 获取所有表
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            print(f"\n📊 数据库中有 {len(tables)} 个表:")
            print("-" * 40)

            for i, table in enumerate(tables, 1):
                table_name = table[0]
                print(f"{i}. {table_name}")

                # 获取表的列信息
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                print(f"   包含列: {', '.join([col[0] for col in columns])}")

            cursor.close()
            connection.close()
            print("\n🔌 数据库连接已关闭")

    except Error as e:
        print(f"❌ 错误: {e}")


# 运行
if __name__ == "__main__":
    check_database_tables()