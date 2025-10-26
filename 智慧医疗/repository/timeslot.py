class TimeslotRepository(Base):
    def get_timeslot_by_time(self, time_str: str) -> Optional[Timeslot]:
        """根据时间获取时间段"""
        query = "SELECT * FROM timeslot WHERE %s BETWEEN starttime AND endtime"

    def get_all_timeslots(self) -> List[Timeslot]:
        """获取所有时间段 """
        query = "SELECT * FROM timeslot"