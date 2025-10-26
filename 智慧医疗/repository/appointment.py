class AppointmentRepository(Base):
    def create_appointment(self, patients_id: int, section_id: int) -> bool:
        """创建预约 - 对应需求5"""
        query = "INSERT INTO appointment (patientsID, sectionID, state) VALUES (%s, %s, 'pending')"

    def cancel_appointment(self, patients_id: int, section_id: int) -> bool:
        """取消预约 - 对应需求6"""
        query = "UPDATE appointment SET state = 'cancelled' WHERE patientsID = %s AND sectionID = %s"

    def get_patient_appointments(self, patients_id: int) -> List[dict]:
        """获取患者所有预约信息 - 对应需求7"""
        query = """
                SELECT a.sectionID, d.*, s.date, t.starttime, t.endtime, a.state
                FROM appointment a
                         JOIN section s ON a.sectionID = s.sectionID
                         JOIN doctor d ON s.doctorID = d.doctorID
                         JOIN timeslot t ON s.timeslotID = t.timeslotID
                WHERE a.patientsID = %s \
                """