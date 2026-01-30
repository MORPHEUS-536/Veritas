"""
SQLAlchemy ORM Models for Dropout Detection System
Maps to PostgreSQL database via NeonDB.
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean, JSON, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Student(Base):
    """Student record for dropout detection."""
    __tablename__ = "dropout_students"

    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    events = relationship("LearningEvent", back_populates="student", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="student", cascade="all, delete-orphan")
    predictions = relationship("DropoutPrediction", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student(id={self.id}, name={self.name})>"


class LearningEvent(Base):
    """Individual learning event (question, submission, etc)."""
    __tablename__ = "dropout_learning_events"

    id = Column(String(50), primary_key=True)
    student_id = Column(String(50), ForeignKey('dropout_students.id'), nullable=False)
    question_id = Column(String(50), nullable=False)
    event_type = Column(String(50), nullable=False)  # QUESTION_START, QUESTION_SUBMIT, etc
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    data = Column(JSON, nullable=True)  # Additional event data
    
    # Relationship
    student = relationship("Student", back_populates="events")

    def __repr__(self):
        return f"<LearningEvent(id={self.id}, event_type={self.event_type})>"


class AttemptHistory(Base):
    """Tracks multiple attempts on a single question."""
    __tablename__ = "dropout_attempt_history"

    id = Column(String(50), primary_key=True)
    student_id = Column(String(50), ForeignKey('dropout_students.id'), nullable=False)
    question_id = Column(String(50), nullable=False)
    attempt_count = Column(Integer, default=0)
    attempt_details = Column(JSON, nullable=True)  # List of attempts with answers, timestamps
    correct_on_first = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<AttemptHistory(question_id={self.question_id}, attempts={self.attempt_count})>"


class Assessment(Base):
    """Assessment/test results for a student."""
    __tablename__ = "dropout_assessments"

    id = Column(String(50), primary_key=True)
    student_id = Column(String(50), ForeignKey('dropout_students.id'), nullable=False)
    subject = Column(String(100), nullable=False)
    topic = Column(String(100))
    score = Column(Float)
    max_score = Column(Float, default=100.0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    student = relationship("Student", back_populates="assessments")

    def __repr__(self):
        return f"<Assessment(student_id={self.student_id}, subject={self.subject})>"


class FeatureSet(Base):
    """Computed feature set for dropout detection (snapshot in time)."""
    __tablename__ = "dropout_feature_sets"

    id = Column(String(50), primary_key=True)
    student_id = Column(String(50), nullable=False)
    
    # Learning Progress Features
    total_questions_attempted = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    average_attempts_per_question = Column(Float, default=0.0)
    learning_velocity = Column(Float, default=0.0)  # Questions completed per day
    
    # Stagnation Features
    days_since_activity = Column(Integer, default=0)
    plateau_duration_days = Column(Integer, default=0)
    answer_stability = Column(Float, default=0.0)  # 0-1, how stable are answers
    
    # Engagement Features
    session_count = Column(Integer, default=0)
    average_session_length_minutes = Column(Float, default=0.0)
    help_requests = Column(Integer, default=0)
    
    # Change Features
    semantic_change_score = Column(Float, default=0.0)  # 0-1
    reasoning_continuity = Column(String(20), default="UNKNOWN")  # HIGH, MEDIUM, LOW
    
    # Timestamps
    computed_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<FeatureSet(student_id={self.student_id})>"


class DropoutPrediction(Base):
    """Dropout prediction result for a student."""
    __tablename__ = "dropout_predictions"

    id = Column(String(50), primary_key=True)
    student_id = Column(String(50), ForeignKey('dropout_students.id'), nullable=False)
    
    # Classification
    dropout_type = Column(String(50))  # COGNITIVE, BEHAVIORAL, ENGAGEMENT, SILENT, NO_DROPOUT
    risk_score = Column(Float)  # 0.0-1.0
    risk_level = Column(String(20))  # LOW, MEDIUM, HIGH, CRITICAL
    
    # Supporting data
    primary_indicators = Column(JSON)  # List of main risk indicators
    secondary_indicators = Column(JSON)  # Supporting indicators
    recommendations = Column(JSON)  # Suggested interventions
    
    # Metadata
    prediction_confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    student = relationship("Student", back_populates="predictions")

    def __repr__(self):
        return f"<DropoutPrediction(student_id={self.student_id}, risk_level={self.risk_level})>"
