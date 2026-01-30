"""
Database initialization and session management for Dropout Detection System.
Uses PostgreSQL via NeonDB for persistent storage.
"""

import os
import logging
from pathlib import Path
from typing import Generator, Optional
from datetime import datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

from db_models import Base, Student, LearningEvent, Assessment, FeatureSet, DropoutPrediction

# Load environment variables from .env file in parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=str(env_path))

logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/veritas_db"
)


class DropoutDatabaseManager:
    """Manages PostgreSQL connections for dropout detection system."""
    
    def __init__(self, db_url: str = DATABASE_URL):
        self.db_url = db_url
        self.engine = None
        self.SessionLocal = None
        self.initialized = False
        
        self._initialize()
    
    def _initialize(self):
        """Initialize database connection."""
        try:
            # Create engine with NullPool for Neon compatibility
            self.engine = create_engine(
                self.db_url,
                echo=os.getenv("DEBUG", "False").lower() == "true",
                poolclass=NullPool,
                future=True
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                bind=self.engine,
                expire_on_commit=False,
                future=True
            )
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            logger.info("Dropout detection database initialized successfully")
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            self.initialized = False
    
    def get_session(self) -> Session:
        """Get a new database session."""
        if not self.initialized:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()
    
    def add_student(self, student_id: str, name: str, email: str) -> Optional[Student]:
        """Add a new student."""
        session = self.get_session()
        try:
            student = Student(id=student_id, name=name, email=email)
            session.add(student)
            session.commit()
            return student
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding student: {str(e)}")
            return None
        finally:
            session.close()
    
    def get_student(self, student_id: str) -> Optional[Student]:
        """Get student by ID."""
        session = self.get_session()
        try:
            return session.execute(
                select(Student).where(Student.id == student_id)
            ).scalars().first()
        except Exception as e:
            logger.error(f"Error getting student: {str(e)}")
            return None
        finally:
            session.close()
    
    def add_learning_event(self, event_id: str, student_id: str, question_id: str, 
                          event_type: str, data: Optional[dict] = None) -> Optional[LearningEvent]:
        """Add a learning event."""
        session = self.get_session()
        try:
            event = LearningEvent(
                id=event_id,
                student_id=student_id,
                question_id=question_id,
                event_type=event_type,
                data=data or {}
            )
            session.add(event)
            session.commit()
            return event
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding learning event: {str(e)}")
            return None
        finally:
            session.close()
    
    def get_student_events(self, student_id: str) -> list:
        """Get all learning events for a student."""
        session = self.get_session()
        try:
            return session.execute(
                select(LearningEvent).where(LearningEvent.student_id == student_id)
                    .order_by(LearningEvent.timestamp)
            ).scalars().all()
        except Exception as e:
            logger.error(f"Error getting student events: {str(e)}")
            return []
        finally:
            session.close()
    
    def add_assessment(self, assessment_id: str, student_id: str, subject: str,
                      score: float, max_score: float = 100.0, topic: str = None) -> Optional[Assessment]:
        """Add an assessment record."""
        session = self.get_session()
        try:
            assessment = Assessment(
                id=assessment_id,
                student_id=student_id,
                subject=subject,
                topic=topic,
                score=score,
                max_score=max_score
            )
            session.add(assessment)
            session.commit()
            return assessment
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding assessment: {str(e)}")
            return None
        finally:
            session.close()
    
    def get_student_assessments(self, student_id: str) -> list:
        """Get all assessments for a student."""
        session = self.get_session()
        try:
            return session.execute(
                select(Assessment).where(Assessment.student_id == student_id)
                    .order_by(Assessment.timestamp)
            ).scalars().all()
        except Exception as e:
            logger.error(f"Error getting assessments: {str(e)}")
            return []
        finally:
            session.close()
    
    def save_feature_set(self, feature_set_id: str, student_id: str, features: dict) -> Optional[FeatureSet]:
        """Save computed feature set."""
        session = self.get_session()
        try:
            feature_obj = FeatureSet(
                id=feature_set_id,
                student_id=student_id,
                **features
            )
            session.add(feature_obj)
            session.commit()
            return feature_obj
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving feature set: {str(e)}")
            return None
        finally:
            session.close()
    
    def save_prediction(self, prediction_id: str, student_id: str, 
                       dropout_type: str, risk_score: float, risk_level: str,
                       indicators: dict = None) -> Optional[DropoutPrediction]:
        """Save dropout prediction."""
        session = self.get_session()
        try:
            prediction = DropoutPrediction(
                id=prediction_id,
                student_id=student_id,
                dropout_type=dropout_type,
                risk_score=risk_score,
                risk_level=risk_level,
                primary_indicators=indicators.get("primary", []) if indicators else [],
                secondary_indicators=indicators.get("secondary", []) if indicators else []
            )
            session.add(prediction)
            session.commit()
            return prediction
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving prediction: {str(e)}")
            return None
        finally:
            session.close()
    
    def get_latest_prediction(self, student_id: str) -> Optional[DropoutPrediction]:
        """Get the latest dropout prediction for a student."""
        session = self.get_session()
        try:
            return session.execute(
                select(DropoutPrediction)
                    .where(DropoutPrediction.student_id == student_id)
                    .order_by(DropoutPrediction.created_at.desc())
                    .limit(1)
            ).scalars().first()
        except Exception as e:
            logger.error(f"Error getting prediction: {str(e)}")
            return None
        finally:
            session.close()


# Global database manager instance
db_manager = DropoutDatabaseManager()


def get_db() -> Generator[Session, None, None]:
    """Dependency function for FastAPI to inject database sessions."""
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()
