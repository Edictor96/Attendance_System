"""
API routes for the attendance system.
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from . import models, schemas, crud, beacon
from .database import get_db
from .config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

def verify_professor_token(authorization: str = Header(...)):
    """Verify professor token from header."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization[7:]
    if token != settings.PROFESSOR_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid professor token")
    
    return token

@router.post("/start_attendance", response_model=schemas.BeaconSession)
def start_attendance(
    session_data: schemas.BeaconSessionCreate,
    db: Session = Depends(get_db),
    token: str = Depends(verify_professor_token)
):
    """Start a new attendance session and emit BLE beacon."""
    try:
        # Create session in database
        db_session = crud.create_beacon_session(db, session_data)
        
        # Start beacon emission (or fallback)
        beacon.start_beacon_emission(db_session.id)
        
        return db_session
    except Exception as e:
        logger.error(f"Error starting attendance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop_attendance", response_model=schemas.BeaconSession)
def stop_attendance(
    session_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(verify_professor_token)
):
    """Stop an active attendance session."""
    try:
        # Stop beacon emission
        beacon.stop_beacon_emission()
        
        # Update session in database
        db_session = crud.update_beacon_session_status(db, session_id, False)
        
        return db_session
    except Exception as e:
        logger.error(f"Error stopping attendance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mark_attendance", response_model=schemas.Attendance)
def mark_attendance(
    attendance_data: schemas.AttendanceCreate,
    db: Session = Depends(get_db)
):
    """Mark attendance for a student."""
    try:
        # Check if session is active
        session = crud.get_beacon_session(db, attendance_data.session_id)
        if not session or not session.is_active:
            raise HTTPException(status_code=400, detail="Session is not active")
        
        # Check for duplicate attendance
        existing = crud.get_attendance_by_student_and_session(
            db, attendance_data.student_id, attendance_data.session_id
        )
        if existing:
            raise HTTPException(status_code=400, detail="Attendance already marked for this session")
        
        # Create attendance record
        attendance = crud.create_attendance(db, attendance_data)
        return attendance
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking attendance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/attendance", response_model=List[schemas.Attendance])
def get_attendance(
    session_id: Optional[int] = None,
    student_id: Optional[str] = None,
    db: Session = Depends(get_db),
    token: str = Depends(verify_professor_token)
):
    """Get attendance records with optional filtering."""
    try:
        attendance = crud.get_attendance(db, session_id, student_id)
        return attendance
    except Exception as e:
        logger.error(f"Error fetching attendance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current_session", response_model=Optional[schemas.BeaconSession])
def get_current_session(db: Session = Depends(get_db)):
    """Get the current active session, if any."""
    try:
        session = crud.get_active_beacon_session(db)
        return session
    except Exception as e:
        logger.error(f"Error getting current session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions", response_model=List[schemas.BeaconSession])
def get_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    token: str = Depends(verify_professor_token)
):
    """Get all beacon sessions."""
    try:
        sessions = crud.get_beacon_sessions(db, skip=skip, limit=limit)
        return sessions
    except Exception as e:
        logger.error(f"Error fetching sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))