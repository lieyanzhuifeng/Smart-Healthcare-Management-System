class RegistrationRepository(Base):
    def create_registration(self, patients_id: int, section_id: int, number: int) -> bool:
        """创建挂号 - 对应需求9,10"""
        query = "INSERT INTO registration (patientsID, sectionID, number, state) VALUES (%s, %s, %s, 'pending')"

    def get_registration_details(self, patients_id: int, section_id: int) -> dict:
        """获取挂号详情 - 对应需求11"""
        query = """
                SELECT d.*, r.number, s.roomID, r.state
                FROM registration r
                         JOIN section s ON r.sectionID = s.sectionID
                         JOIN doctor d ON s.doctorID = d.doctorID
                WHERE r.patientsID = %s \
                  AND r.sectionID = %s \
                """

    def get_patient_registrations(self, patients_id: int) -> List[dict]:
        """获取患者所有挂号信息 - 对应需求12"""
        query = """
                SELECT d.*, r.number, s.roomID, r.state, s.date, t.starttime, t.endtime
                FROM registration r
                         JOIN section s ON r.sectionID = s.sectionID
                         JOIN doctor d ON s.doctorID = d.doctorID
                         JOIN timeslot t ON s.timeslotID = t.timeslotID
                WHERE r.patientsID = %s \
                """