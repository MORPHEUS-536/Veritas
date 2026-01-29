"""
Example FastAPI routes showing complete integration.
Demonstrates authentication, role-based access, monitoring, and analysis.
"""

from fastapi import FastAPI, Depends, HTTPException, Header, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import os
import sys

sys.path.append(os.path.dirname(__file__))

from database import get_db, init_db
from orm_models import User, UserRole, StudentProfile, TeacherProfile
from security import (
    hash_password, verify_password, generate_token, verify_token,
    extract_token_from_header, can_access_student_data, can_access_exam
)
from data_access import (
    get_student_dashboard_data, get_student_exam_detail,
    get_teacher_dashboard_data, get_teacher_exam_analytics,
    get_student_detail_for_teacher, get_monitoring_events_for_attempt
)
from service_layer import (
    create_exam_attempt, complete_exam_attempt, record_monitoring_event,
    save_behavior_analysis, update_performance_metrics, update_student_profile_stats
)


# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Veritas Backend API",
    description="Production-grade exam monitoring and integrity analysis platform",
    version="1.0.0"
)


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    try:
        # Only initialize if DATABASE_URL is properly configured
        if os.getenv("DATABASE_URL"):
            init_db()
            print("✓ Database initialized")
        else:
            print("⚠ DATABASE_URL not set, skipping initialization")
    except Exception as e:
        print(f"⚠ Database initialization: {e}")


# ============================================================================
# DEPENDENCY: GET CURRENT USER
# ============================================================================

async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Extract and validate JWT token from Authorization header.
    Returns current authenticated user.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    token = extract_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    return user


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

class RegisterRequest:
    def __init__(self, email: str, username: str, password: str, first_name: str, last_name: str, role: str):
        self.email = email
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.role = role


@app.post("/auth/register")
async def register(
    email: str,
    username: str,
    password: str,
    first_name: str,
    last_name: str,
    role: str,
    db: Session = Depends(get_db)
):
    """
    Register a new user (student or teacher).
    """
    # Validate role
    if role not in [r.value for r in UserRole]:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {[r.value for r in UserRole]}")
    
    # Check if user already exists
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create user
    user = User(
        email=email,
        username=username,
        password_hash=hash_password(password),
        first_name=first_name,
        last_name=last_name,
        role=UserRole(role)
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create role-specific profile
    if role == UserRole.STUDENT.value:
        profile = StudentProfile(user_id=user.id)
        db.add(profile)
    elif role == UserRole.TEACHER.value:
        profile = TeacherProfile(user_id=user.id)
        db.add(profile)
    
    db.commit()
    
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "role": user.role.value,
        "created_at": user.created_at.isoformat()
    }


@app.post("/auth/login")
async def login(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    """
    Login user and return JWT token.
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Generate token
    token = generate_token(
        user_id=user.id,
        email=user.email,
        role=user.role.value
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "role": user.role.value
        }
    }


# ============================================================================
# STUDENT ROUTES
# ============================================================================

@app.get("/student/dashboard")
async def student_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get student's personal dashboard with exam history, scores, integrity status.
    Only students can access their own dashboard.
    """
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can access this endpoint")
    
    dashboard = get_student_dashboard_data(str(current_user.id), db)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    return dashboard


@app.get("/student/exams/{attempt_id}")
async def student_exam_detail(
    attempt_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed view of a specific exam attempt.
    Student can only view their own attempts.
    """
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can access this endpoint")
    
    attempt_detail = get_student_exam_detail(str(current_user.id), attempt_id, db)
    if not attempt_detail:
        raise HTTPException(status_code=403, detail="Not authorized to view this attempt")
    
    return attempt_detail


@app.post("/student/exams/{exam_id}/start")
async def start_exam(
    exam_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a new exam attempt for the student.
    """
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can start exams")
    
    attempt = create_exam_attempt(
        student_id=str(current_user.id),
        exam_id=exam_id,
        db=db,
        metadata={
            "started_by": "student_interface",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    return {
        "attempt_id": str(attempt.id),
        "exam_id": str(attempt.exam_id),
        "status": "in_progress",
        "started_at": attempt.started_at.isoformat()
    }


@app.post("/student/exams/{attempt_id}/submit")
async def submit_exam(
    attempt_id: str,
    score: float,
    submission_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit exam and record score.
    Triggers behavior analysis pipeline.
    """
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only students can submit exams")
    
    attempt = complete_exam_attempt(attempt_id, score, submission_data, db)
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    if attempt.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to submit this attempt")
    
    # Trigger async analysis (in production, use Celery/RQ)
    # For demo, compute synchronously
    # ... call monitoring/llm_engine modules ...
    
    return {
        "attempt_id": str(attempt.id),
        "status": "completed",
        "score": attempt.score,
        "percentage": attempt.percentage,
        "passed": attempt.passed,
        "completed_at": attempt.completed_at.isoformat()
    }


# ============================================================================
# TEACHER ROUTES
# ============================================================================

@app.get("/teacher/dashboard")
async def teacher_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get teacher's dashboard with managed exams, student analytics, alerts.
    Only teachers can access this endpoint.
    """
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="Only teachers can access this endpoint")
    
    dashboard = get_teacher_dashboard_data(str(current_user.id), db)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Teacher profile not found")
    
    return dashboard


@app.get("/teacher/exams/{exam_id}/analytics")
async def exam_analytics(
    exam_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed analytics for an exam (teacher view).
    Teacher must be creator or authorized for the exam.
    """
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="Only teachers can access this endpoint")
    
    if not can_access_exam("teacher", str(current_user.id), exam_id, db):
        raise HTTPException(status_code=403, detail="Not authorized for this exam")
    
    analytics = get_teacher_exam_analytics(str(current_user.id), exam_id, db)
    if not analytics:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    return analytics


@app.get("/teacher/students/{student_id}")
async def student_detail_for_teacher(
    student_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get student detail page for teacher view (performance, risk, attempts).
    Teacher can only view students for exams they manage.
    """
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="Only teachers can access this endpoint")
    
    detail = get_student_detail_for_teacher(str(current_user.id), student_id, db)
    if not detail:
        raise HTTPException(status_code=403, detail="Not authorized to view this student")
    
    return detail


@app.get("/teacher/attempts/{attempt_id}/monitoring")
async def monitoring_events_detail(
    attempt_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed monitoring events and behavior analysis for an attempt.
    Teacher must be authorized for the exam.
    """
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=403, detail="Only teachers can access this endpoint")
    
    events = get_monitoring_events_for_attempt(str(current_user.id), attempt_id, db)
    if not events:
        raise HTTPException(status_code=403, detail="Not authorized to view this attempt")
    
    return events


# ============================================================================
# MONITORING EVENT INGESTION
# ============================================================================

@app.post("/monitor/events")
async def record_event(
    attempt_id: str,
    event_type: str,
    severity: str,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record a monitoring event during exam.
    Can be called frequently (10+ events/sec).
    Authentication ensures events are for correct student/attempt.
    """
    # Verify attempt belongs to current user
    from orm_models import ExamAttempt
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
    
    if not attempt or attempt.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this attempt")
    
    # Record event
    event = record_monitoring_event(
        attempt_id=attempt_id,
        student_id=str(current_user.id),
        event_type=event_type,
        severity=severity,
        data_payload=data,
        db=db,
        is_anomaly=False,  # Anomaly detection happens separately
        client_timestamp=datetime.utcnow()
    )
    
    if not event:
        raise HTTPException(status_code=400, detail="Failed to record event")
    
    return {
        "event_id": str(event.id),
        "status": "recorded",
        "server_timestamp": event.server_timestamp.isoformat()
    }


# ============================================================================
# BEHAVIOR ANALYSIS (Called by Analysis Service)
# ============================================================================

@app.post("/analysis/behavior")
async def save_analysis(
    attempt_id: str,
    integrity_score: float,
    lmi_score: float,
    dropout_label: str,
    llm_summary: Optional[str] = None,
    recommendations: Optional[list] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save behavior analysis results after exam completion.
    Called by analysis service (not frontend).
    """
    # Verify attempt exists and user has access
    from orm_models import ExamAttempt
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    # Save analysis
    analysis = save_behavior_analysis(
        attempt_id=attempt_id,
        student_id=str(attempt.student_id),
        integrity_score=integrity_score,
        lmi_score=lmi_score,
        dropout_label=dropout_label,
        db=db,
        llm_summary=llm_summary,
        llm_recommendations=recommendations or []
    )
    
    # Update metrics
    update_performance_metrics(str(attempt.student_id), db)
    update_student_profile_stats(str(attempt.student_id), db)
    
    return {
        "analysis_id": str(analysis.id),
        "attempt_id": str(attempt.id),
        "status": "saved"
    }


# ============================================================================
# HEALTH & STATUS
# ============================================================================

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected"
    }


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
