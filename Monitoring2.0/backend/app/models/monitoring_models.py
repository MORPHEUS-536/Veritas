"""
SQLAlchemy ORM Models for Monitoring System
Replaces in-memory database with PostgreSQL persistence via NeonDB.
"""

from datetime import datetime
from enum import Enum
import uuid

from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean, JSON, Enum as SQLEnum, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class HealthStatus(str, Enum):
    """Health status enumeration."""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"


class MonitoringResult(Base):
    """Represents a monitoring analysis result."""
    __tablename__ = "monitoring_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(SQLEnum(HealthStatus), nullable=False)
    analysis_result = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to logs
    logs = relationship("MonitoringLog", back_populates="monitoring_result")

    def __repr__(self):
        return f"<MonitoringResult(id={self.id}, status={self.status})>"


class MonitoringLog(Base):
    """Represents a single monitoring event/log."""
    __tablename__ = "monitoring_logs"

    event_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String(255), nullable=False)  # Data source name
    component = Column(String(255), nullable=True)  # Component being monitored
    message = Column(Text, nullable=True)  # Log message
    
    # Monitoring result reference
    monitoring_result_id = Column(String(36), ForeignKey('monitoring_results.id'), nullable=True)
    monitoring_result = relationship("MonitoringResult", back_populates="logs")
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Additional metadata
    extra_data = Column(JSON, nullable=True)
    
    # Indices for common queries
    __table_args__ = (
        # Index on timestamp for time-based queries
        # Index on source for filtering by data source
        # Index on status for status filtering
    )

    def __repr__(self):
        return f"<MonitoringLog(event_id={self.event_id}, source={self.source})>"


class SystemHealth(Base):
    """Represents overall system health status."""
    __tablename__ = "system_health"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    overall_status = Column(SQLEnum(HealthStatus), nullable=False)
    normal_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    total_logs = Column(Integer, default=0)
    
    # Time window
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<SystemHealth(id={self.id}, overall_status={self.overall_status})>"
