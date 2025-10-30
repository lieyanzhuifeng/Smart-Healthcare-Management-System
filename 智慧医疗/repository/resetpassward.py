import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repository.base import Base


class PasswordResetter(Base):
    """密码重置工具类"""

    def __init__(self):
        super().__init__()

    def reset_all_passwords(self):
        """重置所有人员表的密码为空值"""
        try:
            # 定义所有需要重置密码的表和ID字段
            tables = [
                {"table": "patients", "id_field": "patientsID"},
                {"table": "doctor", "id_field": "doctorID"},
                {"table": "pharmacyman", "id_field": "pharmacymanID"},
                {"table": "admin", "id_field": "adminID"}
            ]

            reset_results = {}

            for table_info in tables:
                table_name = table_info["table"]
                id_field = table_info["id_field"]

                # 检查表是否有password_hash字段
                check_query = """
                              SELECT COUNT(*) as count \
                              FROM information_schema.columns
                              WHERE table_schema = 'hospital_management'
                                AND table_name = %s
                                AND column_name = 'password_hash' \
                              """
                result = self.execute_query(check_query, (table_name,))

                if result and result[0]['count'] > 0:
                    # 重置密码为空字符串
                    reset_query = f"UPDATE {table_name} SET password_hash = NULL"
                    row_count = self.execute_update(reset_query)
                    reset_results[table_name] = {
                        "success": True,
                        "rows_affected": row_count,
                        "message": f"重置了 {row_count} 条记录的密码"
                    }
                    print(f"✅ {table_name}: 重置了 {row_count} 条记录的密码")
                else:
                    reset_results[table_name] = {
                        "success": False,
                        "message": f"表 {table_name} 没有 password_hash 字段"
                    }
                    print(f"⚠️  {table_name}: 没有 password_hash 字段")

            return {
                "success": True,
                "message": "密码重置完成",
                "results": reset_results
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"密码重置失败: {str(e)}"
            }

    def reset_specific_table_passwords(self, table_name: str):
        """重置特定表的密码"""
        try:
            # 检查表是否存在且有password_hash字段
            check_query = """
                          SELECT COUNT(*) as count \
                          FROM information_schema.columns
                          WHERE table_schema = 'hospital_management'
                            AND table_name = %s
                            AND column_name = 'password_hash' \
                          """
            result = self.execute_query(check_query, (table_name,))

            if not result or result[0]['count'] == 0:
                return {
                    "success": False,
                    "message": f"表 {table_name} 不存在或没有 password_hash 字段"
                }

            # 重置密码为空字符串
            reset_query = f"UPDATE {table_name} SET password_hash = NULL"
            row_count = self.execute_update(reset_query)

            return {
                "success": True,
                "message": f"重置了 {row_count} 条记录的密码",
                "rows_affected": row_count
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"重置表 {table_name} 密码失败: {str(e)}"
            }

    def show_current_password_status(self):
        """显示当前各表的密码状态"""
        try:
            tables = ["patients", "doctor", "pharmacyman", "admin"]
            status_results = {}

            for table_name in tables:
                # 检查表是否有password_hash字段
                check_query = """
                              SELECT COUNT(*) as count \
                              FROM information_schema.columns
                              WHERE table_schema = 'hospital_management'
                                AND table_name = %s
                                AND column_name = 'password_hash' \
                              """
                result = self.execute_query(check_query, (table_name,))

                if result and result[0]['count'] > 0:
                    # 统计密码状态
                    status_query = f"""
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN password_hash IS NULL THEN 1 ELSE 0 END) as empty_count,
    SUM(CASE WHEN password_hash IS NOT NULL THEN 1 ELSE 0 END) as has_password_count
FROM {table_name}
                    """
                    status_result = self.execute_query(status_query)

                    if status_result:
                        status_results[table_name] = {
                            "has_password_field": True,
                            "total_records": status_result[0]['total'],
                            "empty_passwords": status_result[0]['empty_count'],
                            "has_passwords": status_result[0]['has_password_count']
                        }
                else:
                    status_results[table_name] = {
                        "has_password_field": False
                    }

            return status_results

        except Exception as e:
            return {"error": f"获取密码状态失败: {str(e)}"}


def main():
    """主函数 - 用于直接运行重置脚本"""
    print("=" * 60)
    print("🔐 密码重置工具")
    print("=" * 60)

    resetter = PasswordResetter()

    # 显示当前状态
    print("\n📊 当前密码状态:")
    status = resetter.show_current_password_status()
    for table, info in status.items():
        if info.get("has_password_field"):
            print(
                f"   {table}: 总记录 {info['total_records']}, 空密码 {info['empty_passwords']}, 有密码 {info['has_passwords']}")
        else:
            print(f"   {table}: 无 password_hash 字段")

    # 确认是否重置
    print("\n⚠️  即将重置所有人员表的密码为空值!")
    confirm = input("确认执行重置操作? (y/N): ")

    if confirm.lower() == 'y':
        print("\n🔄 开始重置密码...")
        result = resetter.reset_all_passwords()

        if result["success"]:
            print("\n✅ 密码重置完成!")
            for table, table_result in result["results"].items():
                if table_result["success"]:
                    print(f"   {table}: {table_result['message']}")
                else:
                    print(f"   {table}: {table_result['message']}")
        else:
            print(f"\n❌ 密码重置失败: {result['message']}")
    else:
        print("\n❌ 操作已取消")

    print("=" * 60)


if __name__ == "__main__":
    main()