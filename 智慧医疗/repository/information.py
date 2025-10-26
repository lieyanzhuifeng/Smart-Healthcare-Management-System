class InformationRepository(Base):
    def get_patient_medical_records(self, patients_id: int) -> List[dict]:
        """获取患者病历 - 对应需求13"""
        query = """
                SELECT i.infID, d.*, i.time, i.information, i.have_medicine
                FROM information i
                         JOIN doctor d ON i.doctorID = d.doctorID
                WHERE i.patientIsD = %s \
                """

    def get_prescription_details(self, inf_id: int) -> List[dict]:
        """获取处方详情 - 对应需求14"""
        query = """
                SELECT m.*, o.amount, o.price
                FROM order_for_medicine o
                         JOIN medicine m ON o.medicineID = m.medicineID
                WHERE o.infID = %s \
                """