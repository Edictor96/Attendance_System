"""
SQLAlchemy models for the attendance system.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Student(Base):
    __tablename__ = "students"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    attendance = relationship("Attendance", back_populates="student")

class BeaconSession(Base):
    __tablename__ = "beacon_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    attendance = relationship("Attendance", back_populates="session")

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("beacon_sessions.id"), nullable=False)
    device_id = Column(String, nullable=False)  # MAC address or hostname
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="attendance")
    session = relationship("BeaconSession", back_populates="attendance")