import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repository.base import Base


def print_table_data():
    """根据用户输入的表名打印整个表 - 循环版本"""

    try:
        # 1. 初始化数据库连接
        print("🔗 初始化数据库连接...")
        db = Base()
        print("✅ 数据库连接成功")

        # 2. 获取所有表名
        print("\n📋 获取数据库中的所有表...")
        tables_result = db.execute_query("SHOW TABLES")
        table_names = [list(table.values())[0] for table in tables_result]

        print(f"✅ 找到 {len(table_names)} 个表:")
        for i, table_name in enumerate(table_names, 1):
            print(f"   {i}. {table_name}")

        # 3. 主循环
        while True:
            print(f"\n" + "=" * 50)
            print("🔍 请输入要查看的表名:")
            print("   - 输入表名查看具体表")
            print("   - 输入 'all' 查看所有表")
            print("   - 输入 'list' 重新显示表列表")
            print("   - 输入 'exit' 或 'quit' 退出程序")
            print("=" * 50)

            user_input = input("请输入: ").strip()

            if user_input.lower() in ['exit', 'quit', 'q']:
                print("👋 再见！")
                break

            elif user_input.lower() == 'list':
                print(f"\n📋 数据库中的所有表:")
                for i, table_name in enumerate(table_names, 1):
                    print(f"   {i}. {table_name}")
                continue

            elif user_input.lower() == 'all':
                tables_to_show = table_names

            else:
                if user_input not in table_names:
                    print(f"❌ 表 '{user_input}' 不存在!")
                    print("💡 请输入正确的表名，或输入 'list' 查看所有表")
                    continue
                tables_to_show = [user_input]

            # 4. 打印每个表的数据
            for table_name in tables_to_show:
                print(f"\n{'=' * 80}")
                print(f"📊 表: {table_name}")
                print(f"{'=' * 80}")

                # 获取表结构
                columns_result = db.execute_query(f"DESCRIBE {table_name}")
                headers = [col['Field'] for col in columns_result]

                # 获取表数据
                data_result = db.execute_query(f"SELECT * FROM {table_name}")

                if not data_result:
                    print("   表为空")
                    continue

                # 打印表头
                print(" | ".join(headers))
                print("-" * 80)

                # 打印数据
                for i, row in enumerate(data_result, 1):
                    values = []
                    for header in headers:
                        value = row.get(header, '')
                        # 处理特殊类型
                        if value is None:
                            values.append("NULL")
                        elif isinstance(value, (bytes, bytearray)):
                            values.append("[BINARY]")
                        else:
                            values.append(str(value))
                    print(f"{i:2d}. | " + " | ".join(values))

                print(f"\n📈 统计: 共 {len(data_result)} 条记录")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print_table_data()