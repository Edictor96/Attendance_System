"""
CRUD operations for database models.
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas

# Student operations
def get_student(db: Session, student_id: str):
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def create_student(db: Session, student: schemas.StudentCreate):
    db_student = models.Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

# BeaconSession operations
def get_beacon_session(db: Session, session_id: int):
    return db.query(models.BeaconSession).filter(models.BeaconSession.id == session_id).first()

def get_active_beacon_session(db: Session):
    return db.query(models.BeaconSession).filter(models.BeaconSession.is_active == True).first()

def get_beacon_sessions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.BeaconSession).offset(skip).limit(limit).all()

def create_beacon_session(db: Session, session: schemas.BeaconSessionCreate):
    db_session = models.BeaconSession(**session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_beacon_session_status(db: Session, session_id: int, is_active: bool):
    db_session = db.query(models.BeaconSession).filter(models.BeaconSession.id == session_id).first()
    if db_session:
        db_session.is_active = is_active
        db.commit()
        db.refresh(db_session)
    return db_session

# Attendance operations
def get_attendance(db: Session, session_id: Optional[int] = None, student_id: Optional[str] = None):
    query = db.query(models.Attendance)
    
    if session_id:
        query = query.filter(models.Attendance.session_id == session_id)
    if student_id:
        query = query.filter(models.Attendance.student_id == student_id)
    
    return query.all()

def get_attendance_by_student_and_session(db: Session, student_id: str, session_id: int):
    return db.query(models.Attendance).filter(
        models.Attendance.student_id == student_id,
        models.Attendance.session_id == session_id
    ).first()

def create_attendance(db: Session, attendance: schemas.AttendanceCreate):
    db_attendance = models.Attendance(**attendance.dict())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance