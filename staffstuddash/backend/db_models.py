"""
SQLAlchemy ORM Models for Staff/Student Dashboard
Maps to PostgreSQL database via NeonDB.
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean, JSON, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Student(Base):
    """Student profile and metadata."""
    __tablename__ = "students"

    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    drafts = relationship("Draft", back_populates="student", cascade="all, delete-orphan")
    assessments = relationship("AssessmentLog", back_populates="student", cascade="all, delete-orphan")
    performance_records = relationship("PerformanceRecord", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student(id={self.id}, name={self.name})>"


class Draft(Base):
    """Student draft submissions."""
    __tablename__ = "drafts"

    id = Column(String(50), primary_key=True)
    student_id = Column(String(50), ForeignKey('students.id'), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    version = Column(Integer, default=1)  # Draft version number
    
    # Relationship
    student = relationship("Student", back_populates="drafts")

    def __repr__(self):
        return f"<Draft(id={self.id}, student_id={self.student_id})>"


class AssessmentLog(Base):
    """Assessment/test scores and results."""
    __tablename__ = "assessment_logs"

    id = Column(String(50), primary_key=True)
    student_id = Column(String(50), ForeignKey('students.id'), nullable=False)
    type = Column(String(50), nullable=False)  # exam, quiz, homework
    subject = Column(String(100), nullable=False)  # Math, Physics, Biology
    topic = Column(String(100), default="General")
    score = Column(Float, nullable=False)
    max_score = Column(Float, default=100.0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    student = relationship("Student", back_populates="assessments")

    def __repr__(self):
        return f"<AssessmentLog(id={self.id}, student_id={self.student_id}, type={self.type})>"


class ConceptModule(Base):
    """Learning concepts being studied."""
    __tablename__ = "concept_modules"

    id = Column(String(50), primary_key=True)
    concept_name = Column(String(255), nullable=False)
    subject = Column(String(100), nullable=False)
    difficulty_level = Column(Integer, default=1)  # 1-5
    attempt_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<ConceptModule(id={self.id}, concept_name={self.concept_name})>"


class PerformanceRecord(Base):
    """Computed performance analytics for a student."""
    __tablename__ = "performance_records"

    id = Column(String(50), primary_key=True)
    student_id = Column(String(50), ForeignKey('students.id'), nullable=False)
    integrity_score = Column(Float, default=0.0)
    grit_level = Column(Float, default=0.0)
    status = Column(String(50), default="Active")  # Active, At Risk, etc.
    
    # Detailed analytics (stored as JSON for flexibility)
    strengths = Column(JSON, default={})  # List of strengths
    weaknesses = Column(JSON, default={})  # List of weaknesses
    subject_scores = Column(JSON, default={})  # Detailed scores per subject
    concept_progress = Column(JSON, default={})  # Progress on concepts
    
    # Flags and alerts
    flags = Column(Boolean, default=False)
    recap_required = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    student = relationship("Student", back_populates="performance_records")

    def __repr__(self):
        return f"<PerformanceRecord(id={self.id}, student_id={self.student_id})>"


class ActionLog(Base):
    """Audit trail of all student actions."""
    __tablename__ = "action_logs"

    id = Column(String(50), primary_key=True)
    student_id = Column(String(50), nullable=False)  # Can exist for deleted students
    action = Column(String(255), nullable=False)
    extra_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ActionLog(id={self.id}, action={self.action})>"
