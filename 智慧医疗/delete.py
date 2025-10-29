# delete_appointment_registration_data.py
import mysql.connector
from mysql.connector import Error
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def delete_appointment_registration_data():
    """删除appointment和registration表中的数据"""
    try:
        # 使用你的数据库连接配置
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

            # 先查看当前数据量
            print("\n📊 删除前数据统计:")

            cursor.execute("SELECT COUNT(*) FROM appointment")
            appointment_count = cursor.fetchone()[0]
            print(f"  appointment表记录数: {appointment_count}")

            cursor.execute("SELECT COUNT(*) FROM registration")
            registration_count = cursor.fetchone()[0]
            print(f"  registration表记录数: {registration_count}")

            if appointment_count == 0 and registration_count == 0:
                print("❌ 两个表都是空的，无需删除")
                return

            # 确认删除
            confirm = input(
                f"\n⚠️  确认要删除 appointment表({appointment_count}条) 和 registration表({registration_count}条) 的所有数据吗？(输入 'DELETE' 确认): ")

            if confirm != 'DELETE':
                print("❌ 删除操作已取消")
                return

            print("\n🔄 开始删除数据...")

            # 删除registration表数据（因为有外键约束，可能需要先处理）
            try:
                # 先禁用外键检查
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

                # 删除registration表数据
                delete_registration_sql = "DELETE FROM registration"
                cursor.execute(delete_registration_sql)
                registration_deleted = cursor.rowcount
                print(f"✅ registration表删除完成: 删除了 {registration_deleted} 条记录")

                # 删除appointment表数据
                delete_appointment_sql = "DELETE FROM appointment"
                cursor.execute(delete_appointment_sql)
                appointment_deleted = cursor.rowcount
                print(f"✅ appointment表删除完成: 删除了 {appointment_deleted} 条记录")

                # 重新启用外键检查
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

                # 提交事务
                connection.commit()

                print(f"\n🎉 数据删除完成!")
                print(f"   - appointment表: 删除了 {appointment_deleted} 条记录")
                print(f"   - registration表: 删除了 {registration_deleted} 条记录")

            except Error as e:
                connection.rollback()
                print(f"❌ 删除过程中出错: {e}")
                raise

            # 验证删除结果
            print("\n📊 删除后数据统计:")
            cursor.execute("SELECT COUNT(*) FROM appointment")
            appointment_after = cursor.fetchone()[0]
            print(f"  appointment表记录数: {appointment_after}")

            cursor.execute("SELECT COUNT(*) FROM registration")
            registration_after = cursor.fetchone()[0]
            print(f"  registration表记录数: {registration_after}")

            cursor.close()
            connection.close()
            print("\n🔌 数据库连接已关闭")

    except Error as e:
        print(f"❌ 数据库错误: {e}")


def delete_specific_patient_data(patient_id):
    """删除特定患者的数据"""
    try:
        connection = mysql.connector.connect(
            host='47.100.240.111',
            database='hospital_management',
            user='root',
            password='Db123456',
            port=3306
        )

        if connection.is_connected():
            print(f"✅ 成功连接到医院管理系统数据库!")

            cursor = connection.cursor()

            # 查看特定患者的数据量
            print(f"\n📊 患者 {patient_id} 的数据统计:")

            cursor.execute("SELECT COUNT(*) FROM appointment WHERE patientsID = %s", (patient_id,))
            appointment_count = cursor.fetchone()[0]
            print(f"  appointment表记录数: {appointment_count}")

            cursor.execute("SELECT COUNT(*) FROM registration WHERE patientsID = %s", (patient_id,))
            registration_count = cursor.fetchone()[0]
            print(f"  registration表记录数: {registration_count}")

            if appointment_count == 0 and registration_count == 0:
                print(f"❌ 患者 {patient_id} 没有相关数据")
                return

            # 确认删除
            confirm = input(
                f"\n⚠️  确认要删除患者 {patient_id} 的预约({appointment_count}条)和挂号({registration_count}条)数据吗？(输入 'DELETE' 确认): ")

            if confirm != 'DELETE':
                print("❌ 删除操作已取消")
                return

            print(f"\n🔄 开始删除患者 {patient_id} 的数据...")

            try:
                # 先删除registration表数据（因为有外键约束）
                delete_registration_sql = "DELETE FROM registration WHERE patientsID = %s"
                cursor.execute(delete_registration_sql, (patient_id,))
                registration_deleted = cursor.rowcount
                print(f"✅ registration表删除完成: 删除了 {registration_deleted} 条记录")

                # 删除appointment表数据
                delete_appointment_sql = "DELETE FROM appointment WHERE patientsID = %s"
                cursor.execute(delete_appointment_sql, (patient_id,))
                appointment_deleted = cursor.rowcount
                print(f"✅ appointment表删除完成: 删除了 {appointment_deleted} 条记录")

                # 提交事务
                connection.commit()

                print(f"\n🎉 患者 {patient_id} 的数据删除完成!")
                print(f"   - appointment表: 删除了 {appointment_deleted} 条记录")
                print(f"   - registration表: 删除了 {registration_deleted} 条记录")

            except Error as e:
                connection.rollback()
                print(f"❌ 删除过程中出错: {e}")
                raise

            cursor.close()
            connection.close()
            print("\n🔌 数据库连接已关闭")

    except Error as e:
        print(f"❌ 数据库错误: {e}")


def reset_auto_increment():
    """重置表的自增ID"""
    try:
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

            # 重置自增ID
            reset_appointment_sql = "ALTER TABLE appointment AUTO_INCREMENT = 1"
            cursor.execute(reset_appointment_sql)
            print("✅ appointment表自增ID重置为1")

            reset_registration_sql = "ALTER TABLE registration AUTO_INCREMENT = 1"
            cursor.execute(reset_registration_sql)
            print("✅ registration表自增ID重置为1")

            connection.commit()

            cursor.close()
            connection.close()
            print("\n🔌 数据库连接已关闭")

    except Error as e:
        print(f"❌ 数据库错误: {e}")


def main():
    """主函数"""
    print("=== 预约和挂号数据清理工具 ===")

    while True:
        print("\n请选择操作:")
        print("1. 删除所有预约和挂号数据")
        print("2. 删除特定患者的预约和挂号数据")
        print("3. 重置自增ID")
        print("4. 退出")

        try:
            choice = input("请输入选择 (1-4): ").strip()

            if choice == '1':
                delete_appointment_registration_data()
            elif choice == '2':
                patient_id = input("请输入患者ID: ").strip()
                if patient_id and patient_id.isdigit():
                    delete_specific_patient_data(int(patient_id))
                else:
                    print("❌ 请输入有效的患者ID")
            elif choice == '3':
                reset_auto_increment()
            elif choice == '4':
                print("退出数据清理工具")
                break
            else:
                print("❌ 无效选择，请重新输入")

        except KeyboardInterrupt:
            print("\n用户取消操作")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    main()