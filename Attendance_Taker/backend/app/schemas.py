"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Student schemas
class StudentBase(BaseModel):
    id: str
    name: str
    email: str

class StudentCreate(StudentBase):
    pass

class Student(StudentBase):
    created_at: datetime
    
    class Config:
        from_attributes = True

# BeaconSession schemas
class BeaconSessionBase(BaseModel):
    name: str
    description: Optional[str] = None

class BeaconSessionCreate(BeaconSessionBase):
    pass

class BeaconSession(BeaconSessionBase):
    id: int
    is_active: bool
    created_at: datetime
    ended_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Attendance schemas
class AttendanceBase(BaseModel):
    student_id: str
    session_id: int
    device_id: str

class AttendanceCreate(AttendanceBase):
    pass

class Attendance(AttendanceBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True