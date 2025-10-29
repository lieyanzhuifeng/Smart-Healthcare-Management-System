# model.py - 医院管理系统数据模型
from typing import List, ClassVar, Optional
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Patients:
    patientsID: int
    name: str
    age: int
    password_hash: str  # 新增：密码哈希字段

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            patientsID=data.get('patientsID'),
            name=data.get('name'),
            age=data.get('age'),
            password_hash=data.get('password_hash', '')  # 默认为空字符串
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
    password_hash: str  # 新增：密码哈希字段

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            doctorID=data.get('doctorID'),
            name=data.get('name'),
            age=data.get('age'),
            expertiseID=data.get('expertiseID'),
            officeID=data.get('officeID'),
            positionID=data.get('positionID'),
            NumberOfPatients=data.get('NumberOfPatients'),
            password_hash=data.get('password_hash', '')  # 默认为空字符串
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
    registrationID: int
    doctorID: int
    patientsID: int
    time: datetime
    have_medicine: bool
    information: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            registrationID=data.get('registrationID'),
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
    registrationID: int
    medicineID: int
    amount: int
    price: float

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            orderID=data.get('orderID'),
            registrationID=data.get('registrationID'),
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


from dataclasses import dataclass
from typing import ClassVar


@dataclass
class Appointment:
    patientsID: int
    sectionID: int
    state: int
    appointmentID: int

    # 状态常量定义
    STATE_ACTIVE: ClassVar[int] = 1  # 有效
    STATE_COMPLETED: ClassVar[int] = 2  # 已完成
    STATE_CANCELLED: ClassVar[int] = 3  # 已取消

    # 状态映射到中文描述
    STATE_DESCRIPTIONS: ClassVar[dict] = {
        1: "有效",
        2: "已完成",
        3: "已取消"
    }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            patientsID=data.get('patientsID'),
            sectionID=data.get('sectionID'),
            state=data.get('state'),
            appointmentID=data.get('appointmentID')
        )

    def get_state_description(self) -> str:
        """获取状态的中文描述"""
        return self.STATE_DESCRIPTIONS.get(self.state, "未知状态")

    def is_active(self) -> bool:
        """检查是否为有效状态"""
        return self.state == self.STATE_ACTIVE

    def is_completed(self) -> bool:
        """检查是否为已完成状态"""
        return self.state == self.STATE_COMPLETED

    def is_cancelled(self) -> bool:
        """检查是否为已取消状态"""
        return self.state == self.STATE_CANCELLED

    def can_be_cancelled(self) -> bool:
        """检查是否可以取消（只有有效状态可以取消）"""
        return self.is_active()

    def can_be_completed(self) -> bool:
        """检查是否可以完成（只有有效状态可以完成）"""
        return self.is_active()


@dataclass
class Registration:
    patientsID: int
    sectionID: int
    number: int
    state: int
    registrationID: int

    # 状态常量定义 - 扩展版
    STATE_REGISTERED: ClassVar[int] = 0      # 已挂号/待就诊
    STATE_IN_PROGRESS: ClassVar[int] = 1     # 就诊中
    STATE_PRESCRIBED: ClassVar[int] = 2      # 已开处方（就诊完成，待取药）
    STATE_MEDICINE_READY: ClassVar[int] = 3  # 药品已准备（药房配药完成）
    STATE_MEDICINE_TAKEN: ClassVar[int] = 4  # 已取药（流程完成）
    STATE_CANCELLED: ClassVar[int] = 5       # 已取消

    # 状态映射到中文描述
    STATE_DESCRIPTIONS: ClassVar[dict] = {
        0: "已挂号/待就诊",
        1: "就诊中",
        2: "已开处方",
        3: "药品已准备",
        4: "已取药/已完成",
        5: "已取消"
    }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            patientsID=data.get('patientsID'),
            sectionID=data.get('sectionID'),
            number=data.get('number'),
            state=data.get('state'),
            registrationID=data.get('registrationID')
        )

    def get_state_description(self) -> str:
        """获取状态的中文描述"""
        return self.STATE_DESCRIPTIONS.get(self.state, "未知状态")

    def is_registered(self) -> bool:
        """检查是否为已挂号状态"""
        return self.state == self.STATE_REGISTERED

    def is_in_progress(self) -> bool:
        """检查是否为就诊中状态"""
        return self.state == self.STATE_IN_PROGRESS

    def is_prescribed(self) -> bool:
        """检查是否为已开处方状态"""
        return self.state == self.STATE_PRESCRIBED

    def is_medicine_ready(self) -> bool:
        """检查是否为药品已准备状态"""
        return self.state == self.STATE_MEDICINE_READY

    def is_medicine_taken(self) -> bool:
        """检查是否为已取药状态"""
        return self.state == self.STATE_MEDICINE_TAKEN

    def is_cancelled(self) -> bool:
        """检查是否为已取消状态"""
        return self.state == self.STATE_CANCELLED

    def can_be_cancelled(self) -> bool:
        """检查是否可以取消（只有已挂号状态可以取消）"""
        return self.is_registered()

    def can_start_visit(self) -> bool:
        """检查是否可以开始就诊（只有已挂号状态可以开始就诊）"""
        return self.is_registered()

    def can_prescribe(self) -> bool:
        """检查是否可以开处方（只有就诊中状态可以开处方）"""
        return self.is_in_progress()

    def can_prepare_medicine(self) -> bool:
        """检查是否可以配药（只有已开处方状态可以配药）"""
        return self.is_prescribed()

    def can_take_medicine(self) -> bool:
        """检查是否可以取药（只有药品已准备状态可以取药）"""
        return self.is_medicine_ready()

    def get_next_possible_states(self) -> List[int]:
        """获取下一个可能的状态"""
        state_transitions = {
            self.STATE_REGISTERED: [self.STATE_IN_PROGRESS, self.STATE_CANCELLED],
            self.STATE_IN_PROGRESS: [self.STATE_PRESCRIBED, self.STATE_CANCELLED],
            self.STATE_PRESCRIBED: [self.STATE_MEDICINE_READY, self.STATE_CANCELLED],
            self.STATE_MEDICINE_READY: [self.STATE_MEDICINE_TAKEN],
            self.STATE_MEDICINE_TAKEN: [],  # 最终状态
            self.STATE_CANCELLED: []        # 最终状态
        }
        return state_transitions.get(self.state, [])


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

@dataclass
class PharmacyMan:
    pharmacymanID: int
    name: str
    age: int
    password_hash: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            pharmacymanID=data.get('pharmacymanID'),
            name=data.get('name'),
            age=data.get('age'),
            password_hash=data.get('password_hash', '')
        )

@dataclass
class Admin:
    adminID: int
    name: str
    age: int
    password_hash: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            adminID=data.get('adminID'),
            name=data.get('name'),
            age=data.get('age'),
            password_hash=data.get('password_hash', '')
        )

# 导出所有模型类
__all__ = [
    'Patients', 'Doctor', 'Expertise', 'Information', 'Medicine',
    'Office', 'OrderForMedicine', 'Pharmacy', 'Position', 'Registration',
    'Room', 'Section', 'Timeslot', 'Appointment', 'DoctorDisplayView',
    'PharmacyMan', 'Admin'  # 新增的两个类
]

