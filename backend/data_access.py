"""
Role-based data access functions for frontend consumption.
Enforces RBAC policies and returns frontend-ready JSON.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(__file__))

from orm_models import (
    User, StudentProfile, TeacherProfile, Exam, ExamAttempt,
    MonitoringEvent, BehaviorAnalysis, PerformanceMetrics,
    UserRole, DropoutRisk, MonitoringStatus
)
from security import can_access_exam, can_access_student_data


# ============================================================================
# STUDENT DATA ACCESS
# ============================================================================

def get_student_dashboard_data(
    student_id: str,
    db: Session
) -> Optional[Dict[str, Any]]:
    """
    Fetch all data visible to student on their dashboard.
    Includes: profile, exam history, integrity status, performance.
    
    Args:
        student_id: UUID of the student
        db: Database session
        
    Returns:
        Dashboard data dict or None if student not found
    """
    student = db.query(User).filter(User.id == student_id).first()
    if not student or student.role != UserRole.STUDENT:
        return None
    
    profile = student.student_profile
    if not profile:
        return None
    
    # Get attempt history
    attempts = db.query(ExamAttempt).filter(
        ExamAttempt.student_id == student_id
    ).order_by(ExamAttempt.started_at.desc()).all()
    
    # Get performance metrics
    metrics = db.query(PerformanceMetrics).filter(
        PerformanceMetrics.student_id == student_id
    ).first()
    
    return {
        "profile": {
            "id": str(student.id),
            "name": f"{student.first_name} {student.last_name}".strip(),
            "email": student.email,
            "enrollment_id": profile.enrollment_id,
            "cohort": profile.cohort,
            "joined_date": student.created_at.isoformat(),
        },
        "integrity": {
            "score": profile.cumulative_integrity_score,
            "status": "good" if profile.cumulative_integrity_score > 0.7 else "warning" if profile.cumulative_integrity_score > 0.4 else "critical"
        },
        "learning_momentum": {
            "lmi": profile.cumulative_lmi,
            "status": "improving" if profile.cumulative_lmi > 50 else "at_risk"
        },
        "dropout_risk": {
            "label": profile.current_dropout_risk.value,
            "flagged": profile.flagged_for_review,
            "confidence": 0.85  # Would come from behavior analysis
        },
        "exam_history": [
            _attempt_to_student_view(attempt) for attempt in attempts
        ],
        "summary": {
            "total_exams": len(attempts),
            "passed": sum(1 for a in attempts if a.passed),
            "pending": sum(1 for a in attempts if a.status == "in_progress"),
            "average_score": metrics.avg_score if metrics else None,
        },
        "performance_metrics": {
            "strengths": metrics.strengths if metrics else [],
            "weaknesses": metrics.weaknesses if metrics else [],
            "subject_scores": metrics.subject_scores if metrics else {},
            "integrity_trend": metrics.integrity_trend if metrics else None,
            "lmi_trend": metrics.lmi_trend if metrics else None,
        }
    }


def get_student_exam_detail(
    student_id: str,
    attempt_id: str,
    db: Session
) -> Optional[Dict[str, Any]]:
    """
    Fetch detailed info for a specific exam attempt (student view).
    
    Args:
        student_id: UUID of the student
        attempt_id: UUID of the exam attempt
        db: Database session
        
    Returns:
        Exam attempt detail or None
    """
    attempt = db.query(ExamAttempt).filter(
        and_(
            ExamAttempt.id == attempt_id,
            ExamAttempt.student_id == student_id
        )
    ).first()
    
    if not attempt:
        return None
    
    behavior = attempt.behavior_record
    
    return {
        "exam": {
            "id": str(attempt.exam.id),
            "title": attempt.exam.title,
            "subject": attempt.exam.subject,
            "topic": attempt.exam.topic,
        },
        "attempt": {
            "id": str(attempt.id),
            "status": attempt.status,
            "score": attempt.score,
            "max_score": attempt.max_score,
            "percentage": attempt.percentage,
            "passed": attempt.passed,
            "started_at": attempt.started_at.isoformat(),
            "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
            "duration_seconds": attempt.duration_seconds,
        },
        "integrity_analysis": {
            "integrity_score": attempt.integrity_score,
            "lmi": attempt.lmi,
            "dropout_label": attempt.dropout_label.value,
            "flagged": attempt.flagged,
        },
        "behavior": {
            "total_events": behavior.total_monitoring_events if behavior else 0,
            "anomalies": behavior.anomaly_count if behavior else 0,
            "critical_events": behavior.critical_events if behavior else 0,
            "originality_indicators": behavior.originality_indicators if behavior else [],
            "llm_summary": behavior.llm_summary if behavior else None,
            "requires_recap": behavior.requires_recap if behavior else False,
        } if behavior else None,
        "monitoring_events_summary": _get_event_summary_for_attempt(attempt_id, db)
    }


def get_available_exams_for_student(db: Session) -> List[Dict[str, Any]]:
    """
    Fetch all published exams available to students.
    
    Args:
        db: Database session
        
    Returns:
        List of exam metadata
    """
    exams = db.query(Exam).filter(Exam.is_published == True).all()
    
    return [
        {
            "id": str(exam.id),
            "title": exam.title,
            "subject": exam.subject,
            "topic": exam.topic,
            "description": exam.description,
            "duration_minutes": exam.duration_minutes,
            "max_score": exam.max_score,
            "passing_score": exam.passing_score,
        }
        for exam in exams
    ]


def _attempt_to_student_view(attempt: ExamAttempt) -> Dict[str, Any]:
    """Convert ExamAttempt to student-visible format."""
    return {
        "id": str(attempt.id),
        "exam_id": str(attempt.exam_id),
        "exam_title": attempt.exam.title,
        "subject": attempt.exam.subject,
        "score": attempt.score,
        "max_score": attempt.max_score,
        "percentage": attempt.percentage,
        "passed": attempt.passed,
        "status": attempt.status,
        "started_at": attempt.started_at.isoformat(),
        "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
        "integrity_score": attempt.integrity_score,
        "dropout_label": attempt.dropout_label.value,
    }


# ============================================================================
# TEACHER DATA ACCESS
# ============================================================================

def get_teacher_dashboard_data(
    teacher_id: str,
    db: Session
) -> Optional[Dict[str, Any]]:
    """
    Fetch teacher dashboard: managed exams, student analytics, anomalies.
    
    Args:
        teacher_id: UUID of the teacher
        db: Database session
        
    Returns:
        Teacher dashboard data or None
    """
    teacher = db.query(User).filter(User.id == teacher_id).first()
    if not teacher or teacher.role != UserRole.TEACHER:
        return None
    
    profile = teacher.teacher_profile
    if not profile:
        return None
    
    # Get exams created by this teacher
    exams = db.query(Exam).filter(Exam.creator_id == teacher_id).all()
    exam_ids = [e.id for e in exams]
    
    if not exam_ids:
        return {
            "profile": _teacher_profile_view(teacher, profile),
            "exams_managed": [],
            "students_overview": None,
            "alerts": []
        }
    
    # Get all attempts for these exams
    all_attempts = db.query(ExamAttempt).filter(
        ExamAttempt.exam_id.in_(exam_ids)
    ).all()
    
    # Get flagged students
    flagged_attempts = [a for a in all_attempts if a.flagged]
    
    # Calculate aggregate stats
    total_students = len(set(a.student_id for a in all_attempts))
    high_risk_students = len(set(
        a.student_id for a in all_attempts 
        if a.dropout_label in [DropoutRisk.COPY, DropoutRisk.INCAPABLE]
    ))
    
    # Get recent critical events
    critical_events = db.query(MonitoringEvent).filter(
        and_(
            MonitoringEvent.exam_attempt_id.in_([a.id for a in all_attempts]),
            MonitoringEvent.severity == MonitoringStatus.CRITICAL
        )
    ).order_by(MonitoringEvent.server_timestamp.desc()).limit(10).all()
    
    return {
        "profile": _teacher_profile_view(teacher, profile),
        "exams_managed": [
            _exam_summary_for_teacher(exam, all_attempts, db)
            for exam in exams
        ],
        "students_overview": {
            "total_students": total_students,
            "high_risk_count": high_risk_students,
            "flagged_count": len(set(a.student_id for a in flagged_attempts)),
            "total_attempts": len(all_attempts),
        },
        "alerts": [
            {
                "type": "anomaly",
                "severity": event.severity.value,
                "event_type": event.event_type,
                "student_id": str(event.student_id),
                "timestamp": event.server_timestamp.isoformat(),
                "description": event.description,
            }
            for event in critical_events
        ]
    }


def get_teacher_exam_analytics(
    teacher_id: str,
    exam_id: str,
    db: Session
) -> Optional[Dict[str, Any]]:
    """
    Fetch detailed analytics for an exam (teacher view).
    Includes per-student performance, integrity scores, anomalies.
    
    Args:
        teacher_id: UUID of the teacher
        exam_id: UUID of the exam
        db: Database session
        
    Returns:
        Exam analytics or None
    """
    # Verify teacher owns or is authorized for this exam
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam or exam.creator_id != teacher_id:
        return None
    
    attempts = db.query(ExamAttempt).filter(
        ExamAttempt.exam_id == exam_id
    ).all()
    
    # Group by student
    students_data = {}
    for attempt in attempts:
        student_id = attempt.student_id
        student = attempt.student
        
        if student_id not in students_data:
            students_data[student_id] = {
                "student_id": str(student_id),
                "name": f"{student.first_name} {student.last_name}".strip(),
                "email": student.email,
                "attempts": [],
            }
        
        students_data[student_id]["attempts"].append({
            "id": str(attempt.id),
            "score": attempt.score,
            "max_score": attempt.max_score,
            "percentage": attempt.percentage,
            "passed": attempt.passed,
            "integrity_score": attempt.integrity_score,
            "lmi": attempt.lmi,
            "dropout_label": attempt.dropout_label.value,
            "flagged": attempt.flagged,
            "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
        })
    
    # Compute exam-level stats
    if attempts:
        avg_score = sum(a.score or 0 for a in attempts) / len(attempts) if attempts else 0
        pass_rate = sum(1 for a in attempts if a.passed) / len(attempts) if attempts else 0
        avg_integrity = sum(a.integrity_score for a in attempts) / len(attempts)
        high_risk = sum(1 for a in attempts if a.dropout_label in [DropoutRisk.COPY, DropoutRisk.INCAPABLE])
    else:
        avg_score = 0
        pass_rate = 0
        avg_integrity = 0
        high_risk = 0
    
    return {
        "exam": {
            "id": str(exam.id),
            "title": exam.title,
            "subject": exam.subject,
            "topic": exam.topic,
            "max_score": exam.max_score,
            "passing_score": exam.passing_score,
            "created_at": exam.created_at.isoformat(),
        },
        "analytics": {
            "total_attempts": len(attempts),
            "unique_students": len(students_data),
            "average_score": round(avg_score, 2),
            "pass_rate": round(pass_rate * 100, 1),
            "average_integrity": round(avg_integrity, 3),
            "high_risk_count": high_risk,
            "flagged_count": sum(1 for a in attempts if a.flagged),
        },
        "students": list(students_data.values()),
        "risk_distribution": {
            "safe": sum(1 for a in attempts if a.dropout_label == DropoutRisk.SAFE),
            "incapable": sum(1 for a in attempts if a.dropout_label == DropoutRisk.INCAPABLE),
            "copy": sum(1 for a in attempts if a.dropout_label == DropoutRisk.COPY),
            "no_interest": sum(1 for a in attempts if a.dropout_label == DropoutRisk.NO_INTEREST),
        }
    }


def get_student_detail_for_teacher(
    teacher_id: str,
    student_id: str,
    db: Session
) -> Optional[Dict[str, Any]]:
    """
    Fetch student profile and performance for teacher view.
    Only allowed if teacher has access via exam assignments.
    
    Args:
        teacher_id: UUID of the teacher
        student_id: UUID of the student
        db: Database session
        
    Returns:
        Student detail or None if not authorized
    """
    if not can_access_student_data("teacher", teacher_id, student_id, db):
        return None
    
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        return None
    
    profile = student.student_profile
    metrics = db.query(PerformanceMetrics).filter(
        PerformanceMetrics.student_id == student_id
    ).first()
    
    # Get teacher's exams this student attempted
    teacher_exams = db.query(Exam).filter(Exam.creator_id == teacher_id).all()
    exam_ids = [e.id for e in teacher_exams]
    
    student_attempts = db.query(ExamAttempt).filter(
        and_(
            ExamAttempt.student_id == student_id,
            ExamAttempt.exam_id.in_(exam_ids)
        )
    ).all()
    
    return {
        "student": {
            "id": str(student.id),
            "name": f"{student.first_name} {student.last_name}".strip(),
            "email": student.email,
            "enrollment_id": profile.enrollment_id if profile else None,
            "cohort": profile.cohort if profile else None,
        },
        "performance": {
            "total_attempts": len(student_attempts),
            "passed": sum(1 for a in student_attempts if a.passed),
            "average_score": metrics.avg_score if metrics else None,
            "strengths": metrics.strengths if metrics else [],
            "weaknesses": metrics.weaknesses if metrics else [],
        },
        "integrity": {
            "cumulative_score": profile.cumulative_integrity_score if profile else 0,
            "current_risk": profile.current_dropout_risk.value if profile else DropoutRisk.SAFE.value,
            "flagged": profile.flagged_for_review if profile else False,
        },
        "attempts": [
            {
                "id": str(a.id),
                "exam_title": a.exam.title,
                "score": a.score,
                "percentage": a.percentage,
                "passed": a.passed,
                "integrity_score": a.integrity_score,
                "dropdown_label": a.dropout_label.value,
                "completed_at": a.completed_at.isoformat() if a.completed_at else None,
            }
            for a in student_attempts
        ]
    }


def get_monitoring_events_for_attempt(
    teacher_id: str,
    attempt_id: str,
    db: Session
) -> Optional[Dict[str, Any]]:
    """
    Fetch detailed monitoring events and analysis for an attempt (teacher view).
    Teacher must be authorized for the exam.
    
    Args:
        teacher_id: UUID of the teacher
        attempt_id: UUID of the exam attempt
        db: Database session
        
    Returns:
        Events and analysis or None if not authorized
    """
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
    if not attempt:
        return None
    
    # Check authorization
    if not can_access_exam("teacher", teacher_id, attempt.exam_id, db):
        return None
    
    # Get events
    events = db.query(MonitoringEvent).filter(
        MonitoringEvent.exam_attempt_id == attempt_id
    ).order_by(MonitoringEvent.server_timestamp.asc()).all()
    
    # Get behavior analysis
    behavior = attempt.behavior_record
    
    # Group events by type and severity
    event_summary = {}
    for event in events:
        key = f"{event.event_type}_{event.severity.value}"
        if key not in event_summary:
            event_summary[key] = {
                "event_type": event.event_type,
                "severity": event.severity.value,
                "count": 0,
                "anomaly_count": 0,
            }
        event_summary[key]["count"] += 1
        if event.is_anomaly:
            event_summary[key]["anomaly_count"] += 1
    
    return {
        "attempt": {
            "id": str(attempt.id),
            "student_name": f"{attempt.student.first_name} {attempt.student.last_name}".strip(),
            "exam_title": attempt.exam.title,
            "score": attempt.score,
            "integrity_score": attempt.integrity_score,
            "status": attempt.status,
        },
        "event_summary": list(event_summary.values()),
        "total_events": len(events),
        "anomaly_events": sum(1 for e in events if e.is_anomaly),
        "critical_events": sum(1 for e in events if e.severity == MonitoringStatus.CRITICAL),
        "events_timeline": [
            {
                "id": str(e.id),
                "timestamp": e.server_timestamp.isoformat(),
                "event_type": e.event_type,
                "severity": e.severity.value,
                "is_anomaly": e.is_anomaly,
                "anomaly_score": e.anomaly_score,
                "description": e.description,
            }
            for e in events
        ],
        "behavior_analysis": {
            "integrity_score": behavior.integrity_score if behavior else attempt.integrity_score,
            "dropout_label": behavior.dropout_label.value if behavior else attempt.dropout_label.value,
            "llm_summary": behavior.llm_summary if behavior else None,
            "recommendations": behavior.llm_recommendations if behavior else [],
            "requires_attention": behavior.requires_instructor_attention if behavior else False,
        } if behavior else None,
    }


def _teacher_profile_view(teacher: User, profile: TeacherProfile) -> Dict[str, Any]:
    """Convert teacher profile to API view."""
    return {
        "id": str(teacher.id),
        "name": f"{teacher.first_name} {teacher.last_name}".strip(),
        "email": teacher.email,
        "department": profile.department,
        "subject_areas": profile.subject_areas,
        "bio": profile.bio,
    }


def _exam_summary_for_teacher(exam: Exam, all_attempts: List[ExamAttempt], db: Session) -> Dict[str, Any]:
    """Get summary of an exam for teacher view."""
    exam_attempts = [a for a in all_attempts if a.exam_id == exam.id]
    
    return {
        "id": str(exam.id),
        "title": exam.title,
        "subject": exam.subject,
        "total_attempts": len(exam_attempts),
        "unique_students": len(set(a.student_id for a in exam_attempts)),
        "average_score": sum(a.score or 0 for a in exam_attempts) / len(exam_attempts) if exam_attempts else 0,
        "pass_rate": sum(1 for a in exam_attempts if a.passed) / len(exam_attempts) if exam_attempts else 0,
        "flagged_count": sum(1 for a in exam_attempts if a.flagged),
        "created_at": exam.created_at.isoformat(),
    }


def _get_event_summary_for_attempt(attempt_id: str, db: Session) -> Dict[str, Any]:
    """Summarize monitoring events for an attempt."""
    events = db.query(MonitoringEvent).filter(
        MonitoringEvent.exam_attempt_id == attempt_id
    ).all()
    
    return {
        "total": len(events),
        "by_type": {},
        "by_severity": {
            "normal": sum(1 for e in events if e.severity == MonitoringStatus.NORMAL),
            "warning": sum(1 for e in events if e.severity == MonitoringStatus.WARNING),
            "critical": sum(1 for e in events if e.severity == MonitoringStatus.CRITICAL),
        },
        "anomalies": sum(1 for e in events if e.is_anomaly),
    }
