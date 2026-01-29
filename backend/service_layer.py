"""
Service layer for managing exam attempts, monitoring events, and behavior analysis.
Integrates with existing monitoring and LLM scoring modules.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import uuid
import sys
import os

sys.path.append(os.path.dirname(__file__))

from orm_models import (
    ExamAttempt, MonitoringEvent, BehaviorAnalysis, PerformanceMetrics,
    StudentProfile, Exam, User, DropoutRisk, MonitoringStatus
)


# ============================================================================
# EXAM ATTEMPT MANAGEMENT
# ============================================================================

def create_exam_attempt(
    student_id: str,
    exam_id: str,
    db: Session,
    metadata: Dict[str, Any] = None
) -> Optional[ExamAttempt]:
    """
    Create a new exam attempt for a student.
    
    Args:
        student_id: UUID of the student
        exam_id: UUID of the exam
        db: Database session
        metadata: Additional metadata (client info, IP, etc.)
        
    Returns:
        Created ExamAttempt or None if validation fails
    """
    # Verify student and exam exist
    student = db.query(User).filter(User.id == student_id).first()
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    
    if not student or not exam:
        return None
    
    attempt = ExamAttempt(
        id=uuid.uuid4(),
        exam_id=exam_id,
        student_id=student_id,
        max_score=exam.max_score,
        status="in_progress",
        metadata=metadata or {}
    )
    
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    return attempt


def complete_exam_attempt(
    attempt_id: str,
    score: float,
    submission_data: Dict[str, Any],
    db: Session
) -> Optional[ExamAttempt]:
    """
    Mark exam attempt as completed and record score.
    
    Args:
        attempt_id: UUID of the attempt
        score: Final score obtained
        submission_data: Submission content/responses
        db: Database session
        
    Returns:
        Updated ExamAttempt or None
    """
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
    if not attempt:
        return None
    
    attempt.status = "completed"
    attempt.score = score
    attempt.percentage = (score / attempt.max_score * 100) if attempt.max_score > 0 else 0
    attempt.passed = attempt.percentage >= attempt.exam.passing_score
    attempt.completed_at = datetime.utcnow()
    attempt.submission_data = submission_data
    
    if attempt.started_at:
        attempt.duration_seconds = int((attempt.completed_at - attempt.started_at).total_seconds())
    
    db.commit()
    db.refresh(attempt)
    
    return attempt


def abandon_exam_attempt(attempt_id: str, db: Session) -> Optional[ExamAttempt]:
    """Mark attempt as abandoned (student disconnected/timeout)."""
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
    if not attempt:
        return None
    
    attempt.status = "abandoned"
    if attempt.started_at and not attempt.completed_at:
        attempt.completed_at = datetime.utcnow()
        attempt.duration_seconds = int((attempt.completed_at - attempt.started_at).total_seconds())
    
    db.commit()
    db.refresh(attempt)
    
    return attempt


# ============================================================================
# MONITORING EVENT INGESTION
# ============================================================================

def record_monitoring_event(
    attempt_id: str,
    student_id: str,
    event_type: str,
    severity: str,
    data_payload: Dict[str, Any],
    db: Session,
    is_anomaly: bool = False,
    anomaly_score: float = None,
    description: str = None,
    client_timestamp: datetime = None
) -> Optional[MonitoringEvent]:
    """
    Record a real-time monitoring event during exam.
    Non-blocking: can be called frequently without performance impact.
    
    Args:
        attempt_id: UUID of the exam attempt
        student_id: UUID of the student
        event_type: Type of event (eye_movement, window_focus, etc.)
        severity: Event severity (normal/warning/critical)
        data_payload: Raw event data (sensor readings, etc.)
        db: Database session
        is_anomaly: Whether event is flagged as anomaly
        anomaly_score: Confidence score for anomaly (0-1)
        description: Human-readable description
        client_timestamp: When event occurred on client
        
    Returns:
        Created MonitoringEvent or None
    """
    # Validate severity
    if severity not in [s.value for s in MonitoringStatus]:
        return None
    
    event = MonitoringEvent(
        id=uuid.uuid4(),
        exam_attempt_id=attempt_id,
        student_id=student_id,
        event_type=event_type,
        severity=MonitoringStatus(severity),
        data_payload=data_payload,
        is_anomaly=is_anomaly,
        anomaly_score=anomaly_score,
        description=description,
        client_timestamp=client_timestamp,
        server_timestamp=datetime.utcnow()
    )
    
    db.add(event)
    
    # Batch commit: if there are many pending inserts, commit in batches
    try:
        db.commit()
        db.refresh(event)
    except Exception as e:
        db.rollback()
        print(f"Error recording monitoring event: {e}")
        return None
    
    return event


def get_attempt_monitoring_events(
    attempt_id: str,
    db: Session,
    limit: int = 1000,
    offset: int = 0
) -> List[MonitoringEvent]:
    """
    Fetch monitoring events for an attempt with pagination.
    
    Args:
        attempt_id: UUID of the attempt
        db: Database session
        limit: Number of events to fetch
        offset: Pagination offset
        
    Returns:
        List of MonitoringEvent records
    """
    return db.query(MonitoringEvent).filter(
        MonitoringEvent.exam_attempt_id == attempt_id
    ).order_by(
        MonitoringEvent.server_timestamp.asc()
    ).offset(offset).limit(limit).all()


def get_anomalous_events(
    attempt_id: str,
    db: Session,
    severity: Optional[str] = None
) -> List[MonitoringEvent]:
    """Fetch anomalous events for an attempt, optionally filtered by severity."""
    query = db.query(MonitoringEvent).filter(
        and_(
            MonitoringEvent.exam_attempt_id == attempt_id,
            MonitoringEvent.is_anomaly == True
        )
    )
    
    if severity:
        query = query.filter(MonitoringEvent.severity == MonitoringStatus(severity))
    
    return query.order_by(MonitoringEvent.server_timestamp.asc()).all()


# ============================================================================
# BEHAVIOR ANALYSIS & SCORING
# ============================================================================

def save_behavior_analysis(
    attempt_id: str,
    student_id: str,
    integrity_score: float,
    lmi_score: float,
    dropout_label: str,
    db: Session,
    dropdown_confidence: float = 0.85,
    llm_summary: str = None,
    llm_recommendations: List[str] = None,
    originality_indicators: List[str] = None,
    requires_recap: bool = False,
    metadata: Dict[str, Any] = None
) -> Optional[BehaviorAnalysis]:
    """
    Save computed behavior analysis for an exam attempt.
    Called after monitoring analysis is complete.
    
    Args:
        attempt_id: UUID of the exam attempt
        student_id: UUID of the student
        integrity_score: Computed integrity score (0-1)
        lmi_score: Learning Momentum Index
        dropout_label: Dropout risk classification
        db: Database session
        dropdown_confidence: Confidence in dropout classification
        llm_summary: Natural language analysis from LLM
        llm_recommendations: List of recommendations
        originality_indicators: Indicators of originality/plagiarism
        requires_recap: Whether recap is needed
        metadata: Additional metadata
        
    Returns:
        Created BehaviorAnalysis or None
    """
    # Verify attempt exists
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
    if not attempt:
        return None
    
    # Count events for this attempt
    event_count = db.query(func.count(MonitoringEvent.id)).filter(
        MonitoringEvent.exam_attempt_id == attempt_id
    ).scalar()
    
    anomaly_count = db.query(func.count(MonitoringEvent.id)).filter(
        and_(
            MonitoringEvent.exam_attempt_id == attempt_id,
            MonitoringEvent.is_anomaly == True
        )
    ).scalar()
    
    critical_count = db.query(func.count(MonitoringEvent.id)).filter(
        and_(
            MonitoringEvent.exam_attempt_id == attempt_id,
            MonitoringEvent.severity == MonitoringStatus.CRITICAL
        )
    ).scalar()
    
    behavior = BehaviorAnalysis(
        id=uuid.uuid4(),
        exam_attempt_id=attempt_id,
        student_id=student_id,
        total_monitoring_events=event_count,
        anomaly_count=anomaly_count,
        critical_events=critical_count,
        integrity_score=integrity_score,
        lmi_score=lmi_score,
        dropout_label=DropoutRisk(dropout_label),
        dropout_confidence=dropdown_confidence,
        originality_indicators=originality_indicators or [],
        llm_summary=llm_summary,
        llm_recommendations=llm_recommendations or [],
        requires_recap=requires_recap,
        requires_instructor_attention=(critical_count > 0 or dropout_label in [DropoutRisk.COPY.value, DropoutRisk.INCAPABLE.value]),
        metadata=metadata or {}
    )
    
    db.add(behavior)
    
    # Update attempt with analysis results
    attempt.integrity_score = integrity_score
    attempt.lmi = lmi_score
    attempt.dropout_label = DropoutRisk(dropout_label)
    attempt.flagged = behavior.requires_instructor_attention
    
    db.commit()
    db.refresh(behavior)
    
    return behavior


# ============================================================================
# PERFORMANCE METRICS AGGREGATION
# ============================================================================

def update_performance_metrics(student_id: str, db: Session) -> Optional[PerformanceMetrics]:
    """
    Recompute and update performance metrics for a student.
    Aggregates all exam attempts, behavior analysis, etc.
    Called after exam completion or on demand.
    
    Args:
        student_id: UUID of the student
        db: Database session
        
    Returns:
        Updated PerformanceMetrics or None
    """
    # Get or create metrics record
    metrics = db.query(PerformanceMetrics).filter(
        PerformanceMetrics.student_id == student_id
    ).first()
    
    if not metrics:
        metrics = PerformanceMetrics(id=uuid.uuid4(), student_id=student_id)
        db.add(metrics)
    
    # Fetch all completed attempts for this student
    attempts = db.query(ExamAttempt).filter(
        and_(
            ExamAttempt.student_id == student_id,
            ExamAttempt.status == "completed"
        )
    ).all()
    
    if not attempts:
        db.commit()
        return metrics
    
    # Calculate basic stats
    total_passed = sum(1 for a in attempts if a.passed)
    scores = [a.score for a in attempts if a.score is not None]
    
    metrics.total_attempts = len(attempts)
    metrics.total_passed = total_passed
    metrics.avg_score = sum(scores) / len(scores) if scores else None
    
    # Calculate subject-based performance
    subject_scores = {}
    for attempt in attempts:
        subject = attempt.exam.subject
        if subject not in subject_scores:
            subject_scores[subject] = []
        
        pct = (attempt.score / attempt.max_score * 100) if attempt.max_score > 0 else 0
        subject_scores[subject].append(pct)
    
    subject_averages = {s: sum(scores) / len(scores) for s, scores in subject_scores.items()}
    
    if subject_averages:
        max_avg = max(subject_averages.values())
        min_avg = min(subject_averages.values())
        
        metrics.strengths = [s for s, avg in subject_averages.items() if avg == max_avg]
        metrics.weaknesses = [s for s, avg in subject_averages.items() if avg == min_avg and avg < max_avg]
    
    metrics.subject_scores = subject_averages
    
    # Calculate integrity trends
    integrity_scores = [a.integrity_score for a in attempts]
    if integrity_scores:
        metrics.avg_integrity_score = sum(integrity_scores) / len(integrity_scores)
        
        if len(integrity_scores) >= 2:
            trend = integrity_scores[-1] - integrity_scores[-2]
            if trend > 0.05:
                metrics.integrity_trend = "improving"
            elif trend < -0.05:
                metrics.integrity_trend = "declining"
            else:
                metrics.integrity_trend = "stable"
    
    # Calculate LMI trends
    lmi_scores = [a.lmi for a in attempts]
    if lmi_scores:
        metrics.avg_lmi = sum(lmi_scores) / len(lmi_scores)
        
        if len(lmi_scores) >= 2:
            trend = lmi_scores[-1] - lmi_scores[-2]
            if trend > 5:
                metrics.lmi_trend = "improving"
            elif trend < -5:
                metrics.lmi_trend = "declining"
            else:
                metrics.lmi_trend = "stable"
    
    # Determine overall risk
    recent_attempts = attempts[-3:] if len(attempts) >= 3 else attempts
    high_risk_count = sum(1 for a in recent_attempts if a.dropout_label in [
        DropoutRisk.COPY, DropoutRisk.INCAPABLE
    ])
    
    if high_risk_count >= 2:
        metrics.current_risk_label = DropoutRisk.INCAPABLE if all(
            a.integrity_score < 0.5 for a in recent_attempts
        ) else DropoutRisk.COPY
        metrics.flagged_for_intervention = True
    else:
        metrics.current_risk_label = DropoutRisk.SAFE
        metrics.flagged_for_intervention = False
    
    if attempts:
        metrics.last_attempt_date = max(a.completed_at for a in attempts if a.completed_at)
    
    db.commit()
    db.refresh(metrics)
    
    return metrics


def update_student_profile_stats(student_id: str, db: Session) -> Optional[StudentProfile]:
    """
    Update student profile with aggregated stats.
    Called after exam completion.
    
    Args:
        student_id: UUID of the student
        db: Database session
        
    Returns:
        Updated StudentProfile or None
    """
    profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == student_id
    ).first()
    
    if not profile:
        return None
    
    # Get metrics
    metrics = db.query(PerformanceMetrics).filter(
        PerformanceMetrics.student_id == student_id
    ).first()
    
    if metrics:
        profile.cumulative_integrity_score = metrics.avg_integrity_score or 1.0
        profile.cumulative_lmi = metrics.avg_lmi or 0.0
        profile.total_exams_attempted = metrics.total_attempts
        profile.total_exams_passed = metrics.total_passed
        profile.current_dropout_risk = metrics.current_risk_label
        profile.flagged_for_review = metrics.flagged_for_intervention
    
    db.commit()
    db.refresh(profile)
    
    return profile


# ============================================================================
# BATCH OPERATIONS FOR ANALYTICS
# ============================================================================

def get_flagged_students_for_exam(
    exam_id: str,
    db: Session
) -> List[Tuple[User, ExamAttempt, Optional[BehaviorAnalysis]]]:
    """
    Get all flagged students for an exam.
    Used for teacher notifications and interventions.
    
    Args:
        exam_id: UUID of the exam
        db: Database session
        
    Returns:
        List of (User, ExamAttempt, BehaviorAnalysis) tuples
    """
    attempts = db.query(ExamAttempt).filter(
        and_(
            ExamAttempt.exam_id == exam_id,
            ExamAttempt.flagged == True
        )
    ).all()
    
    results = []
    for attempt in attempts:
        behavior = attempt.behavior_record
        results.append((attempt.student, attempt, behavior))
    
    return results


def get_high_risk_events_summary(
    days: int = 7,
    db: Session = None
) -> Dict[str, Any]:
    """
    Aggregate high-risk events from the past N days.
    Used for system monitoring and teacher alerts.
    
    Args:
        days: Number of days to look back
        db: Database session
        
    Returns:
        Summary of high-risk events
    """
    from datetime import timedelta
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    critical_events = db.query(MonitoringEvent).filter(
        and_(
            MonitoringEvent.server_timestamp >= cutoff,
            MonitoringEvent.severity == MonitoringStatus.CRITICAL
        )
    ).all()
    
    anomalies = db.query(MonitoringEvent).filter(
        and_(
            MonitoringEvent.server_timestamp >= cutoff,
            MonitoringEvent.is_anomaly == True
        )
    ).all()
    
    return {
        "period_days": days,
        "critical_event_count": len(critical_events),
        "anomaly_count": len(anomalies),
        "affected_students": len(set(e.student_id for e in critical_events + anomalies)),
        "affected_exams": len(set(
            db.query(ExamAttempt.exam_id).filter(
                ExamAttempt.id.in_(set(e.exam_attempt_id for e in critical_events + anomalies))
            )
        )),
    }
