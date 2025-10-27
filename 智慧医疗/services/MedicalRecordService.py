import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, Dict, Any
from datetime import datetime
from model import DoctorDisplayView, Medicine, OrderForMedicine
from repository.information import InformationRepository


class MedicalRecordService:
    def __init__(self):
        self.information_repo = InformationRepository()

    def get_patient_medical_records(self, patients_id: int) -> List[Dict[str, Any]]:
        """
        获取患者完整病历记录
        包含病历基本信息和医生详细信息
        """
        try:
            # 调用 repository 获取病历记录
            medical_records = self.information_repo.get_patient_medical_records(patients_id)

            # 转换为字典格式，方便服务层处理
            result_records = []
            for record in medical_records:
                # 将 MedicalRecordView 对象转换为字典
                record_dict = {
                    'infID': record.infID,
                    'time': record.time,
                    'information': record.information,
                    'have_medicine': record.have_medicine,
                    'doctor': record.doctor
                }

                # 如果有药品信息，则获取处方详情
                if record.have_medicine:
                    inf_id = record.infID
                    prescription_details = self.get_prescription_details(inf_id)
                    record_dict['prescription'] = prescription_details
                else:
                    record_dict['prescription'] = []

                result_records.append(record_dict)

            return result_records

        except Exception as e:
            print(f"服务层获取患者病历时出错: {e}")
            return []

    def get_prescription_details(self, inf_id: int) -> List[dict]:
        """
        获取处方详情
        """
        try:
            return self.information_repo.get_prescription_details(inf_id)
        except Exception as e:
            print(f"服务层获取处方详情时出错: {e}")
            return []

    def get_medical_record_summary(self, patients_id: int) -> Dict[str, Any]:
        """
        获取患者病历摘要统计
        """
        try:
            records = self.get_patient_medical_records(patients_id)

            total_records = len(records)
            records_with_medicine = len([r for r in records if r.get('have_medicine', False)])
            recent_record = records[0] if records else None

            summary = {
                'patient_id': patients_id,
                'total_records': total_records,
                'records_with_medicine': records_with_medicine,
                'recent_record_time': recent_record.get('time') if recent_record else None,
            }

            # 添加医生信息
            if recent_record and recent_record.get('doctor'):
                summary['recent_doctor'] = recent_record['doctor'].doctor_name
            else:
                summary['recent_doctor'] = None

            return summary

        except Exception as e:
            print(f"获取病历摘要时出错: {e}")
            return {}
