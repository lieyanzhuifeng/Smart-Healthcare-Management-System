# model.py - 医院管理系统数据模型
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Patient:
    patientsID: int
    name: str
    age: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            patientsID=data.get('patientsID'),
            name=data.get('name'),
            age=data.get('age')
        )


@dataclass
class Doctor:
    doctorID: int
    name: str
    age: int
    expertiseID: int
    officeID: int
    positionID: int
    NumberOfPatients: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            doctorID=data.get('doctorID'),
            name=data.get('name'),
            age=data.get('age'),
            expertiseID=data.get('expertiseID'),
            officeID=data.get('officeID'),
            positionID=data.get('positionID'),
            NumberOfPatients=data.get('NumberOfPatients')
        )


@dataclass
class Expertise:
    expertiseID: int
    name: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            expertiseID=data.get('expertiseID'),
            name=data.get('name')
        )


@dataclass
class Information:
    infID: int
    doctorID: int
    patientsID: int
    time: datetime
    have_medicine: bool
    information: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            infID=data.get('infID'),
            doctorID=data.get('doctorID'),
            patientsID=data.get('patientsID'),
            time=data.get('time'),
            have_medicine=bool(data.get('have_medicine')),
            information=data.get('information')
        )


@dataclass
class Medicine:
    medicineID: int
    name: str
    price: float
    description: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            medicineID=data.get('medicineID'),
            name=data.get('name'),
            price=float(data.get('price', 0)),
            description=data.get('description')
        )


@dataclass
class Office:
    officeID: int
    name: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            officeID=data.get('officeID'),
            name=data.get('name')
        )


@dataclass
class OrderForMedicine:
    orderID: int
    infID: int
    medicineID: int
    amount: int
    price: float

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            orderID=data.get('orderID'),
            infID=data.get('infID'),
            medicineID=data.get('medicineID'),
            amount=data.get('amount'),
            price=float(data.get('price', 0))
        )


@dataclass
class Pharmacy:
    medicineID: int
    number: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            medicineID=data.get('medicineID'),
            number=data.get('number')
        )


@dataclass
class Position:
    positionID: int
    name: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            positionID=data.get('positionID'),
            name=data.get('name')
        )


@dataclass
class Registration:
    patientsID: int
    sectionID: int
    number: int
    state: int
    registrationID: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            patientsID=data.get('patientsID'),
            sectionID=data.get('sectionID'),
            number=data.get('number'),
            state=data.get('state'),
            registrationID=data.get('registrationID')
        )


@dataclass
class Room:
    roomID: int
    officeID: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            roomID=data.get('roomID'),
            officeID=data.get('officeID')
        )


@dataclass
class Section:
    doctorID: int
    date: datetime
    roomID: int
    timeslotID: int
    sectionID: int
    restappiontment: int
    appiontmentconvert: int
    restregistration: int
    totalregistration: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            doctorID=data.get('doctorID'),
            date=data.get('date'),
            roomID=data.get('roomID'),
            timeslotID=data.get('timeslotID'),
            sectionID=data.get('sectionID'),
            restappiontment=data.get('restappiontment'),
            appiontmentconvert=data.get('appiontmentconvert'),
            restregistration=data.get('restregistration'),
            totalregistration=data.get('totalregistration')
        )


@dataclass
class Timeslot:
    timeslotID: int
    starttime: str
    endtime: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            timeslotID=data.get('timeslotID'),
            starttime=data.get('starttime'),
            endtime=data.get('endtime')
        )


@dataclass
class Appointment:
    patientsID: int
    sectionID: int
    state: int
    appointmentID: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            patientsID=data.get('patientsID'),
            sectionID=data.get('sectionID'),
            state=data.get('state'),
            appointmentID=data.get('appointmentID')
        )


@dataclass
class DoctorDisplayView:
    """医生显示视图模型"""
    doctorID: int
    doctor_name: str
    age: int
    office_name: str
    expertise_name: str
    position_name: str
    NumberOfPatients: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            doctorID=data.get('doctorID'),
            doctor_name=data.get('doctor_name'),
            age=data.get('age'),
            office_name=data.get('office_name'),
            expertise_name=data.get('expertise_name'),
            position_name=data.get('position_name'),
            NumberOfPatients=data.get('NumberOfPatients')
        )



# 导出所有模型类
__all__ = [
    'Patient',
    'Doctor',
    'Expertise',
    'Information',
    'Medicine',
    'Office',
    'OrderForMedicine',
    'Pharmacy',
    'Position',
    'Registration',
    'Room',
    'Section',
    'Timeslot',
    'Appointment'
    'DoctorDisplayView'
]