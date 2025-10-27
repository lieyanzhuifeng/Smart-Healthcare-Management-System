import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
from datetime import datetime, timedelta
from typing import List, Dict
from repository.doctor import DoctorRepository
from repository.room import RoomRepository
from repository.section import SectionRepository


class DoctorScheduleService:
    def __init__(self):
        self.doctor_repo = DoctorRepository()
        self.room_repo = RoomRepository()
        self.section_repo = SectionRepository()

    #根据日期范围，自动生成排班数据，但不保存进数据库
    def generate_schedules(self, start_date: str, end_date: str, timeslots: List[int] = [1, 2, 3, 4]) -> List[Dict]:
        """生成指定日期范围的排班"""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")

            all_schedules = []
            current_date = start

            while current_date <= end:
                date_str = current_date.strftime("%Y-%m-%d")
                daily_schedules = self._generate_daily_schedule(date_str, timeslots)
                all_schedules.extend(daily_schedules)
                current_date += timedelta(days=1)

            print(f"✅ 成功生成 {len(all_schedules)} 条排班记录")
            return all_schedules

        except Exception as e:
            print(f"❌ 生成排班失败: {e}")
            return []

    def _generate_daily_schedule(self, date: str, timeslots: List[int]) -> List[Dict]:
        """生成单日排班"""
        daily_schedules = []

        try:
            # 获取所有医生，然后按科室分组
            all_doctors = self.doctor_repo.get_all_doctors()

            # 按科室分组医生
            doctors_by_office = {}
            for doctor in all_doctors:
                office_id = doctor.officeID
                if office_id not in doctors_by_office:
                    doctors_by_office[office_id] = []
                doctors_by_office[office_id].append(doctor)

            # 为每个科室生成排班
            for office_id, doctors in doctors_by_office.items():
                # 获取该科室的房间
                rooms = self.room_repo.get_rooms_by_office(office_id)

                if not rooms:
                    print(f"⚠️ 科室 {office_id} 没有房间，跳过排班")
                    continue

                x = len(doctors)  # 医生数量
                y = len(rooms)  # 房间数量

                for timeslot_id in timeslots:
                    slot_schedules = self._schedule_office_timeslot(
                        doctors, rooms, date, timeslot_id, x, y
                    )
                    daily_schedules.extend(slot_schedules)

            return daily_schedules

        except Exception as e:
            print(f"❌ 生成单日排班失败: {e}")
            return []

    def _schedule_office_timeslot(self, doctors: List, rooms: List, date: str,
                                  timeslot_id: int, x: int, y: int) -> List[Dict]:
        """安排一个科室在一个时间段的排班"""
        schedules = []

        try:
            if x <= y:
                # 医生少，房间多：按房间顺序依次排医生
                for i, doctor in enumerate(doctors):
                    if i < len(rooms):
                        room = rooms[i]
                        schedule = self._create_schedule_entry(
                            doctor.doctorID, date, room.roomID, timeslot_id
                        )
                        schedules.append(schedule)
            else:
                # 医生多，房间少：随机选择y个医生
                selected_doctors = random.sample(doctors, y)
                for i, doctor in enumerate(selected_doctors):
                    room = rooms[i]
                    schedule = self._create_schedule_entry(
                        doctor.doctorID, date, room.roomID, timeslot_id
                    )
                    schedules.append(schedule)

            return schedules

        except Exception as e:
            print(f"❌ 安排科室时间段排班失败: {e}")
            return []

    def _create_schedule_entry(self, doctor_id: int, date: str, room_id: int, timeslot_id: int) -> Dict:
        """创建排班记录数据"""


        return {
            'doctorID': doctor_id,
            'date': date,
            'roomID': room_id,
            'timeslotID': timeslot_id,
        }

    def save_schedules_to_database(self, schedules: List[Dict]) -> bool:
        """将排班保存到数据库"""
        try:
            if not schedules:
                print("⚠️ 没有排班数据需要保存")
                return False

            success_count = 0
            for schedule in schedules:
                success = self.section_repo.create_section(
                    doctor_id=schedule['doctorID'],
                    date=schedule['date'],
                    room_id=schedule['roomID'],
                    timeslot_id=schedule['timeslotID'],
                )
                if success:
                    success_count += 1

            print(f"✅ 成功保存 {success_count}/{len(schedules)} 条排班记录到数据库")
            return success_count == len(schedules)

        except Exception as e:
            print(f"❌ 保存排班到数据库失败: {e}")
            return False

    # 根据日期范围，自动生成排班数据，并且保存进数据库
    def generate_and_save_schedules(self, start_date: str, end_date: str, timeslots: List[int] = [1, 2, 3, 4]) -> bool:
        """生成并保存排班（一站式服务）- 智能防重复"""
        try:
            # 生成排班
            schedules = self.generate_schedules(start_date, end_date, timeslots)

            if not schedules:
                print("⚠️ 没有生成任何排班记录")
                return False

            # 智能过滤：只添加不冲突的新排班
            filtered_schedules = self._filter_conflicting_schedules(schedules)

            if not filtered_schedules:
                print("✅ 所有排班时段已被占用，无需重复生成")
                return True

            print(f"📊 排班生成统计:")
            print(f"   - 理论排班数: {len(schedules)}")
            print(f"   - 实际可添加: {len(filtered_schedules)}")
            print(f"   - 跳过重复: {len(schedules) - len(filtered_schedules)}")

            # 保存到数据库
            return self.save_schedules_to_database(filtered_schedules)

        except Exception as e:
            print(f"❌ 生成并保存排班失败: {e}")
            return False

    def _filter_conflicting_schedules(self, schedules: List[Dict]) -> List[Dict]:
        """过滤掉冲突的排班（医生-日期-时间段冲突）"""
        filtered = []

        for schedule in schedules:
            doctor_id = schedule['doctorID']
            date = schedule['date']
            timeslot_id = schedule['timeslotID']

            # 检查该医生在该日期该时间段是否已有排班
            existing_sections = self.section_repo.get_sections_by_doctor_and_date(doctor_id, date)

            # 检查时间段冲突
            timeslot_conflict = any(
                section.timeslotID == timeslot_id
                for section in existing_sections
            )

            if not timeslot_conflict:
                filtered.append(schedule)
            else:
                print(f"⚠️ 跳过冲突排班: 医生{doctor_id} 在{date} 时段{timeslot_id} 已有排班")

        return filtered

    def clear_schedules(self, start_date: str, end_date: str) -> bool:
        """清除指定日期范围的排班"""
        try:
            # 获取该日期范围的排班
            sections = self.section_repo.get_sections_by_date_range(start_date, end_date)

            if not sections:
                print(f"⚠️ 日期范围 {start_date} 到 {end_date} 没有排班记录")
                return True

            success_count = 0
            for section in sections:
                success = self.section_repo.delete_section(section.sectionID)
                if success:
                    success_count += 1

            print(f"✅ 成功删除 {success_count}/{len(sections)} 条排班记录")
            return success_count == len(sections)

        except Exception as e:
            print(f"❌ 清除排班失败: {e}")
            return False