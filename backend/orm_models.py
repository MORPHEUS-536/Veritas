"""
SQLAlchemy ORM models for Veritas platform.
Defines database schema for users, exams, monitoring, and analysis.
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey,
    JSON, Enum, UUID, Text, Index, CheckConstraint, UniqueConstraint,
    func, event
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
import enum

from database import Base


# ============================================================================
# ENUMS
# ============================================================================

class UserRole(str, enum.Enum):
    """User role enumeration."""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class DropoutRisk(str, enum.Enum):
    """Dropout risk classification."""
    SAFE = "safe"
    INCAPABLE = "incapable"
    COPY = "copy"
    NO_INTEREST = "no_interest"


class MonitoringStatus(str, enum.Enum):
    """Monitoring event status."""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"


# ============================================================================
# CORE USERS & AUTHENTICATION
# ============================================================================

class User(Base):
    """
    Core user model for both students and teachers.
    Supports multi-role assignment (though typically one per user).
    """
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    password_hash = Column(String(255), nullable=False)  # bcrypt hash
    role = Column(Enum(UserRole), nullable=False, index=True)
    
    # Account status
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)
    verification_token_expires_at = Column(DateTime, nullable=True)
    
    # Authentication tracking
    last_login = Column(DateTime, nullable=True)
    last_login_ip = Column(String(45), nullable=True)  # IPv6 compatible
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Additional metadata
    meta_data = Column(JSONB, default={}, nullable=False)  # Profile image URL, bio, etc.

    # Relationships
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    teacher_profile = relationship("TeacherProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    exam_attempts = relationship("ExamAttempt", back_populates="student", foreign_keys="ExamAttempt.student_id", cascade="all, delete-orphan")
    monitoring_events = relationship("MonitoringEvent", back_populates="student", cascade="all, delete-orphan")
    behavior_records = relationship("BehaviorAnalysis", back_populates="student", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_users_email_role", "email", "role"),
        Index("idx_users_active_role", "is_active", "role"),
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class StudentProfile(Base):
    """
    Extended student profile information.
    Links to User with role='student'.
    """
    __tablename__ = "student_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Academic info
    enrollment_id = Column(String(50), nullable=True)  # Institutional ID
    cohort = Column(String(100), nullable=True)  # E.g., "2024-Q1"
    
    # Performance tracking
    cumulative_integrity_score = Column(Float, default=1.0, nullable=False)  # 0-1 scale
    cumulative_lmi = Column(Float, default=0.0, nullable=False)  # Learning Momentum Index
    total_exams_attempted = Column(Integer, default=0, nullable=False)
    total_exams_passed = Column(Integer, default=0, nullable=False)
    
    # Risk assessment
    current_dropout_risk = Column(Enum(DropoutRisk), default=DropoutRisk.SAFE, nullable=False, index=True)
    flagged_for_review = Column(Boolean, default=False, index=True)
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="student_profile")

    __table_args__ = (
        Index("idx_student_dropout_risk", "current_dropout_risk"),
        Index("idx_student_flagged", "flagged_for_review"),
    )

    def __repr__(self):
        return f"<StudentProfile(user_id={self.user_id}, dropout_risk={self.current_dropout_risk})>"


class TeacherProfile(Base):
    """
    Extended teacher profile information.
    Links to User with role='teacher'.
    """
    __tablename__ = "teacher_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Professional info
    department = Column(String(100), nullable=True)
    subject_areas = Column(JSON, default=[], nullable=False)  # ['Math', 'Physics']
    credentials = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Permissions & management
    can_create_exams = Column(Boolean, default=True, nullable=False)
    can_view_analytics = Column(Boolean, default=True, nullable=False)
    can_manage_students = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="teacher_profile")
    exams = relationship("Exam", back_populates="creator", foreign_keys="Exam.creator_id")
    test_authorized_exams = relationship(
        "Exam",
        secondary="teacher_exam_permissions",
        back_populates="authorized_teachers"
    )

    def __repr__(self):
        return f"<TeacherProfile(user_id={self.user_id}, department={self.department})>"


# ============================================================================
# EXAM MANAGEMENT
# ============================================================================

class Exam(Base):
    """
    Represents a single exam/assessment.
    Created by teachers, attempted by students.
    """
    __tablename__ = "exams"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    subject = Column(String(100), nullable=False, index=True)
    topic = Column(String(100), nullable=True)
    
    # Assessment parameters
    max_score = Column(Float, default=100.0, nullable=False)
    duration_minutes = Column(Integer, nullable=False)  # Time limit
    passing_score = Column(Float, default=60.0, nullable=False)
    
    # Configuration
    is_published = Column(Boolean, default=False, index=True)
    enable_monitoring = Column(Boolean, default=True, nullable=False)
    enable_integrity_analysis = Column(Boolean, default=True, nullable=False)
    meta_data = Column(JSONB, default={}, nullable=False)  # Custom fields, rules, etc.
    
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    creator = relationship("User", foreign_keys=[creator_id])
    exam_attempts = relationship("ExamAttempt", back_populates="exam", cascade="all, delete-orphan")
    authorized_teachers = relationship(
        "TeacherProfile",
        secondary="teacher_exam_permissions",
        back_populates="test_authorized_exams"
    )

    __table_args__ = (
        Index("idx_exam_creator_published", "creator_id", "is_published"),
        Index("idx_exam_subject_topic", "subject", "topic"),
    )

    def __repr__(self):
        return f"<Exam(id={self.id}, title={self.title}, subject={self.subject})>"


class TeacherExamPermission(Base):
    """
    Maps teachers to exams they can view/manage.
    Enables role-based data access control (RBAC).
    """
    __tablename__ = "teacher_exam_permissions"

    teacher_id = Column(PG_UUID(as_uuid=True), ForeignKey("teacher_profiles.id", ondelete="CASCADE"), primary_key=True)
    exam_id = Column(PG_UUID(as_uuid=True), ForeignKey("exams.id", ondelete="CASCADE"), primary_key=True)
    
    can_view = Column(Boolean, default=True, nullable=False)
    can_edit = Column(Boolean, default=True, nullable=False)
    can_view_analytics = Column(Boolean, default=True, nullable=False)
    granted_at = Column(DateTime, default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_teacher_exams", "teacher_id"),
        Index("idx_exam_teachers", "exam_id"),
    )


class ExamAttempt(Base):
    """
    Represents a student's attempt at an exam.
    Links student to exam, contains attempt metadata and scores.
    """
    __tablename__ = "exam_attempts"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_id = Column(PG_UUID(as_uuid=True), ForeignKey("exams.id"), nullable=False, index=True)
    student_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Attempt status
    status = Column(String(50), default="in_progress", nullable=False)  # in_progress, completed, abandoned
    score = Column(Float, nullable=True)
    max_score = Column(Float, nullable=False)
    percentage = Column(Float, nullable=True)  # (score / max_score) * 100
    passed = Column(Boolean, nullable=True)
    
    # Integrity metrics (computed by monitoring/analysis)
    integrity_score = Column(Float, default=1.0, nullable=False)  # 0-1 scale
    lmi = Column(Float, default=0.0, nullable=False)  # Learning Momentum Index
    dropout_label = Column(Enum(DropoutRisk), default=DropoutRisk.SAFE, nullable=False, index=True)
    flagged = Column(Boolean, default=False, index=True)
    
    # Timestamps
    started_at = Column(DateTime, default=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)  # Actual time taken
    
    # Flexible storage for submissions, drafts, responses
    submission_data = Column(JSONB, default={}, nullable=False)  # Raw responses, drafts, etc.
    meta_data = Column(JSONB, default={}, nullable=False)  # Client info, browser, IP, etc.

    # Relationships
    exam = relationship("Exam", back_populates="exam_attempts")
    student = relationship("User", back_populates="exam_attempts", foreign_keys=[student_id])
    monitoring_events = relationship("MonitoringEvent", back_populates="exam_attempt", cascade="all, delete-orphan")
    behavior_record = relationship("BehaviorAnalysis", back_populates="exam_attempt", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_attempt_exam_student", "exam_id", "student_id"),
        Index("idx_attempt_student_status", "student_id", "status"),
        Index("idx_attempt_dropout_risk", "dropout_label"),
        Index("idx_attempt_flagged", "flagged"),
        CheckConstraint("score >= 0 AND score <= max_score", name="ck_attempt_score_valid"),
    )

    def __repr__(self):
        return f"<ExamAttempt(id={self.id}, student_id={self.student_id}, exam_id={self.exam_id}, status={self.status})>"


# ============================================================================
# MONITORING & REAL-TIME EVENTS
# ============================================================================

class MonitoringEvent(Base):
    """
    Represents a single real-time monitoring event during an exam attempt.
    Captures suspicious behavior, anomalies, performance metrics.
    """
    __tablename__ = "monitoring_events"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_attempt_id = Column(PG_UUID(as_uuid=True), ForeignKey("exam_attempts.id"), nullable=False, index=True)
    student_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Event classification
    event_type = Column(String(100), nullable=False, index=True)  # eye_movement, window_focus, etc.
    severity = Column(Enum(MonitoringStatus), default=MonitoringStatus.NORMAL, nullable=False, index=True)
    
    # Event details
    description = Column(Text, nullable=True)
    data_payload = Column(JSONB, nullable=False)  # Raw event data, sensor readings, etc.
    
    # Analysis
    is_anomaly = Column(Boolean, default=False, index=True)
    anomaly_score = Column(Float, nullable=True)  # Confidence 0-1
    analysis_notes = Column(Text, nullable=True)
    
    # Metadata
    client_timestamp = Column(DateTime, nullable=True)
    server_timestamp = Column(DateTime, default=func.now(), nullable=False, index=True)

    # Relationships
    exam_attempt = relationship("ExamAttempt", back_populates="monitoring_events")
    student = relationship("User", back_populates="monitoring_events", foreign_keys=[student_id])

    __table_args__ = (
        Index("idx_event_attempt", "exam_attempt_id"),
        Index("idx_event_student", "student_id"),
        Index("idx_event_type_severity", "event_type", "severity"),
        Index("idx_event_anomaly", "is_anomaly"),
    )

    def __repr__(self):
        return f"<MonitoringEvent(id={self.id}, type={self.event_type}, severity={self.severity})>"


# ============================================================================
# BEHAVIOR & LLM ANALYSIS
# ============================================================================

class BehaviorAnalysis(Base):
    """
    Aggregated behavior analysis for an exam attempt.
    Computed post-attempt using LLM and rule-based engines.
    """
    __tablename__ = "behavior_analysis"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_attempt_id = Column(PG_UUID(as_uuid=True), ForeignKey("exam_attempts.id"), unique=True, nullable=False, index=True)
    student_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Aggregated metrics
    total_monitoring_events = Column(Integer, default=0, nullable=False)
    anomaly_count = Column(Integer, default=0, nullable=False)
    critical_events = Column(Integer, default=0, nullable=False)
    
    # Thinking quality & originality
    integrity_score = Column(Float, nullable=False)  # 0-1
    originality_indicators = Column(JSON, default=[], nullable=False)  # List of findings
    
    # Learning progress
    lmi_score = Column(Float, nullable=False)
    improvement_trend = Column(String(50), nullable=True)  # improving, stagnant, declining
    
    # Dropout classification
    dropout_label = Column(Enum(DropoutRisk), nullable=False, index=True)
    dropout_confidence = Column(Float, nullable=False)  # 0-1
    
    # LLM Analysis output
    llm_summary = Column(Text, nullable=True)  # Natural language summary
    llm_recommendations = Column(JSON, default=[], nullable=False)  # Action items
    llm_model_version = Column(String(50), nullable=True)  # Track which LLM version
    
    # Flags
    requires_instructor_attention = Column(Boolean, default=False, index=True)
    requires_recap = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    analysis_completed_at = Column(DateTime, default=func.now(), nullable=False)
    meta_data = Column(JSONB, default={}, nullable=False)

    # Relationships
    exam_attempt = relationship("ExamAttempt", back_populates="behavior_record")
    student = relationship("User", back_populates="behavior_records", foreign_keys=[student_id])

    __table_args__ = (
        Index("idx_behavior_attempt", "exam_attempt_id"),
        Index("idx_behavior_student", "student_id"),
        Index("idx_behavior_dropout", "dropout_label"),
        Index("idx_behavior_flagged", "requires_instructor_attention"),
    )

    def __repr__(self):
        return f"<BehaviorAnalysis(id={self.id}, dropout={self.dropout_label}, flagged={self.requires_instructor_attention})>"


class PerformanceMetrics(Base):
    """
    Aggregated performance metrics per student.
    Denormalized for fast dashboard queries.
    """
    __tablename__ = "performance_metrics"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    
    # Cumulative scores
    total_attempts = Column(Integer, default=0, nullable=False)
    total_passed = Column(Integer, default=0, nullable=False)
    avg_score = Column(Float, nullable=True)
    
    # Subject performance
    strengths = Column(JSON, default=[], nullable=False)  # List of subjects/topics
    weaknesses = Column(JSON, default=[], nullable=False)
    subject_scores = Column(JSONB, default={}, nullable=False)  # {"Math": 85, "Physics": 72}
    
    # Integrity
    avg_integrity_score = Column(Float, nullable=True)
    integrity_trend = Column(String(50), nullable=True)  # improving, stable, declining
    
    # Learning momentum
    avg_lmi = Column(Float, nullable=True)
    lmi_trend = Column(String(50), nullable=True)
    
    # Overall risk
    current_risk_label = Column(Enum(DropoutRisk), default=DropoutRisk.SAFE, nullable=False, index=True)
    flagged_for_intervention = Column(Boolean, default=False, index=True)
    
    # Timestamps
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    last_attempt_date = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_perf_student_risk", "student_id", "current_risk_label"),
        Index("idx_perf_flagged", "flagged_for_intervention"),
    )

    def __repr__(self):
        return f"<PerformanceMetrics(student_id={self.student_id}, risk={self.current_risk_label})>"


# ============================================================================
# AUDIT & LOGGING
# ============================================================================

class AuditLog(Base):
    """
    Audit trail for sensitive operations.
    Tracks data access, modifications for compliance.
    """
    __tablename__ = "audit_logs"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(255), nullable=False)  # "login", "view_student_data", "modify_exam"
    resource_type = Column(String(100), nullable=False)  # "user", "exam_attempt", "behavior_analysis"
    resource_id = Column(String(100), nullable=True)
    
    details = Column(JSONB, default={}, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)

    __table_args__ = (
        Index("idx_audit_user_action", "user_id", "action"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
    )
