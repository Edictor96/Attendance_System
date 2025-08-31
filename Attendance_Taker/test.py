"""
Tests for the FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.database import Base, get_db
from backend.app.config import settings

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(app)

# Test data
TEST_PROFESSOR_TOKEN = "test_professor_token"
TEST_STUDENT_ID = "test_student_123"
TEST_DEVICE_ID = "test_device_abc"

@pytest.fixture(scope="function")
def test_db():
    """Create test database and tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_start_attendance_no_token(test_db):
    """Test starting attendance without token."""
    response = client.post(
        "/api/v1/start_attendance",
        json={"name": "Test Session", "description": "Test Description"}
    )
    assert response.status_code == 401

def test_start_attendance_with_token(test_db):
    """Test starting attendance with token."""
    response = client.post(
        "/api/v1/start_attendance",
        json={"name": "Test Session", "description": "Test Description"},
        headers={"Authorization": f"Bearer {TEST_PROFESSOR_TOKEN}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Session"
    assert response.json()["is_active"] == True

def test_mark_attendance(test_db):
    """Test marking attendance."""
    # First create a session
    session_response = client.post(
        "/api/v1/start_attendance",
        json={"name": "Test Session", "description": "Test Description"},
        headers={"Authorization": f"Bearer {TEST_PROFESSOR_TOKEN}"}
    )
    session_id = session_response.json()["id"]
    
    # Mark attendance
    attendance_data = {
        "student_id": TEST_STUDENT_ID,
        "session_id": session_id,
        "device_id": TEST_DEVICE_ID
    }
    response = client.post(
        "/api/v1/mark_attendance",
        json=attendance_data
    )
    assert response.status_code == 200
    assert response.json()["student_id"] == TEST_STUDENT_ID

def test_mark_duplicate_attendance(test_db):
    """Test marking duplicate attendance."""
    # First create a session
    session_response = client.post(
        "/api/v1/start_attendance",
        json={"name": "Test Session", "description": "Test Description"},
        headers={"Authorization": f"Bearer {TEST_PROFESSOR_TOKEN}"}
    )
    session_id = session_response.json()["id"]
    
    # Mark attendance first time
    attendance_data = {
        "student_id": TEST_STUDENT_ID,
        "session_id": session_id,
        "device_id": TEST_DEVICE_ID
    }
    response1 = client.post("/api/v1/mark_attendance", json=attendance_data)
    assert response1.status_code == 200
    
    # Try to mark again
    response2 = client.post("/api/v1/mark_attendance", json=attendance_data)
    assert response2.status_code == 400
    assert "already marked" in response2.json()["detail"]

def test_get_attendance(test_db):
    """Test getting attendance records."""
    # First create a session and mark attendance
    session_response = client.post(
        "/api/v1/start_attendance",
        json={"name": "Test Session", "description": "Test Description"},
        headers={"Authorization": f"Bearer {TEST_PROFESSOR_TOKEN}"}
    )
    session_id = session_response.json()["id"]
    
    attendance_data = {
        "student_id": TEST_STUDENT_ID,
        "session_id": session_id,
        "device_id": TEST_DEVICE_ID
    }
    client.post("/api/v1/mark_attendance", json=attendance_data)
    
    # Get attendance
    response = client.get(
        "/api/v1/attendance",
        headers={"Authorization": f"Bearer {TEST_PROFESSOR_TOKEN}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["student_id"] == TEST_STUDENT_ID

def test_get_current_session(test_db):
    """Test getting current active session."""
    # No active session initially
    response = client.get("/api/v1/current_session")
    assert response.status_code == 200
    assert response.json() is None
    
    # Create a session
    client.post(
        "/api/v1/start_attendance",
        json={"name": "Test Session", "description": "Test Description"},
        headers={"Authorization": f"Bearer {TEST_PROFESSOR_TOKEN}"}
    )
    
    # Now should have active session
    response = client.get("/api/v1/current_session")
    assert response.status_code == 200
    assert response.json() is not None
    assert response.json()["is_active"] == True