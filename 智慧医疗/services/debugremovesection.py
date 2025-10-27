import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repository.section import SectionRepository


def clear_section_table_skip_deps():
    """清空section表，跳过有外键依赖的记录"""
    print("清空section表（跳过有外键依赖的记录）...")

    try:
        section_repo = SectionRepository()

        # 1. 先获取总记录数
        count_query = "SELECT COUNT(*) as count FROM section"
        total_result = section_repo.execute_query(count_query)
        total_count = total_result[0]['count'] if total_result else 0

        print(f"section表总记录数: {total_count} 条")

        if total_count == 0:
            print("section表已经是空的，无需清空")
            return True

        # 2. 找出有外键依赖的section记录
        print("🔍 检查外键依赖...")

        # 找出被appointment表引用的section
        appointment_deps = section_repo.execute_query("""
                                                      SELECT DISTINCT s.sectionID
                                                      FROM section s
                                                               JOIN appointment a ON s.sectionID = a.sectionID
                                                      """)

        # 找出被registration表引用的section
        registration_deps = section_repo.execute_query("""
                                                       SELECT DISTINCT s.sectionID
                                                       FROM section s
                                                                JOIN registration r ON s.sectionID = r.sectionID
                                                       """)

        # 合并所有有依赖的sectionID
        dependent_section_ids = set()
        for dep in appointment_deps:
            dependent_section_ids.add(dep['sectionID'])
        for dep in registration_deps:
            dependent_section_ids.add(dep['sectionID'])

        print(f"发现 {len(dependent_section_ids)} 条记录有外键依赖")

        # 3. 只删除没有依赖的记录
        if dependent_section_ids:
            # 构建NOT IN查询
            placeholders = ', '.join(['%s'] * len(dependent_section_ids))
            delete_query = f"DELETE FROM section WHERE sectionID NOT IN ({placeholders})"
            result = section_repo.execute_update(delete_query, tuple(dependent_section_ids))
        else:
            # 如果没有依赖，删除所有记录
            delete_query = "DELETE FROM section"
            result = section_repo.execute_update(delete_query)

        print(f"✅ 成功删除 {result} 条无依赖的记录")
        print(f"📊 保留了 {len(dependent_section_ids)} 条有依赖的记录")

        return True

    except Exception as e:
        print(f"❌ 清空section表失败: {e}")
        return False


if __name__ == "__main__":
    clear_section_table_skip_deps()