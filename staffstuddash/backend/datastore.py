# Database Storage - PostgreSQL via NeonDB
# In-memory fallback for development/hackathon (if DB unavailable)

import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

from db_models import Base, Student, Draft, AssessmentLog, PerformanceRecord, ActionLog, ConceptModule

# Load environment variables from .env file in parent directory
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=str(env_path))

logger = logging.getLogger(__name__)

# Get database URL from environment or use local PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/veritas_db"
)

# Global storage fallback (if DB unavailable)
students_fallback = {}
drafts_fallback = {}
assessments_fallback = []
performance_records_fallback = {}


class DatastoreManager:
    """
    Manages persistent data storage using PostgreSQL.
    Falls back to in-memory storage if database is unavailable.
    """
    
    def __init__(self, db_url: str = DATABASE_URL):
        self.db_url = db_url
        self.engine = None
        self.SessionLocal = None
        self.use_fallback = False
        
        self._initialize_db()
    
    def _initialize_db(self):
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
            logger.info("PostgreSQL database initialized successfully")
            
        except Exception as e:
            logger.warning(f"PostgreSQL connection failed: {str(e)}. Using in-memory fallback.")
            self.use_fallback = True
    
    def get_session(self) -> Session:
        """Get a database session."""
        if self.use_fallback or not self.SessionLocal:
            return None
        return self.SessionLocal()
    
    # ==================== STUDENT OPERATIONS ====================
    
    def add_student(self, student_id: str, name: str, email: str) -> Dict:
        """Add a new student."""
        if self.use_fallback:
            students_fallback[student_id] = {"id": student_id, "name": name, "email": email}
            return students_fallback[student_id]
        
        session = self.get_session()
        try:
            student = Student(id=student_id, name=name, email=email)
            session.add(student)
            session.commit()
            return {"id": student.id, "name": student.name, "email": student.email}
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding student: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_student(self, student_id: str) -> Optional[Dict]:
        """Get student by ID."""
        if self.use_fallback:
            return students_fallback.get(student_id)
        
        session = self.get_session()
        try:
            student = session.execute(
                select(Student).where(Student.id == student_id)
            ).scalars().first()
            
            if student:
                return {"id": student.id, "name": student.name, "email": student.email}
            return None
        except Exception as e:
            logger.error(f"Error getting student: {str(e)}")
            return None
        finally:
            session.close()
    
    # ==================== DRAFT OPERATIONS ====================
    
    def add_draft(self, student_id: str, draft_id: str, text: str) -> Dict:
        """Add a student draft."""
        if self.use_fallback:
            drafts_fallback[draft_id] = {
                "id": draft_id,
                "student_id": student_id,
                "text": text,
                "timestamp": datetime.now().isoformat()
            }
            return drafts_fallback[draft_id]
        
        session = self.get_session()
        try:
            draft = Draft(id=draft_id, student_id=student_id, text=text)
            session.add(draft)
            session.commit()
            return {
                "id": draft.id,
                "student_id": draft.student_id,
                "text": draft.text,
                "timestamp": draft.timestamp.isoformat()
            }
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding draft: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_drafts_by_student(self, student_id: str) -> List[Dict]:
        """Get all drafts for a student."""
        if self.use_fallback:
            return [d for d in drafts_fallback.values() if d["student_id"] == student_id]
        
        session = self.get_session()
        try:
            drafts = session.execute(
                select(Draft).where(Draft.student_id == student_id)
            ).scalars().all()
            
            return [{
                "id": d.id,
                "student_id": d.student_id,
                "text": d.text,
                "timestamp": d.timestamp.isoformat()
            } for d in drafts]
        except Exception as e:
            logger.error(f"Error getting drafts: {str(e)}")
            return []
        finally:
            session.close()
    
    # ==================== ASSESSMENT OPERATIONS ====================
    
    def add_assessment(self, student_id: str, type: str, subject: str, score: float, max_score: float = 100.0) -> Dict:
        """Add an assessment record."""
        assessment_id = str(uuid.uuid4())
        
        if self.use_fallback:
            assessment = {
                "id": assessment_id,
                "student_id": student_id,
                "type": type,
                "subject": subject,
                "score": score,
                "max_score": max_score,
                "timestamp": datetime.now().isoformat()
            }
            assessments_fallback.append(assessment)
            return assessment
        
        session = self.get_session()
        try:
            assessment = AssessmentLog(
                id=assessment_id,
                student_id=student_id,
                type=type,
                subject=subject,
                score=score,
                max_score=max_score
            )
            session.add(assessment)
            session.commit()
            return {
                "id": assessment.id,
                "student_id": assessment.student_id,
                "type": assessment.type,
                "subject": assessment.subject,
                "score": assessment.score,
                "max_score": assessment.max_score,
                "timestamp": assessment.timestamp.isoformat()
            }
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding assessment: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_assessments_by_student(self, student_id: str) -> List[Dict]:
        """Get all assessments for a student."""
        if self.use_fallback:
            return [a for a in assessments_fallback if a["student_id"] == student_id]
        
        session = self.get_session()
        try:
            assessments = session.execute(
                select(AssessmentLog).where(AssessmentLog.student_id == student_id)
            ).scalars().all()
            
            return [{
                "id": a.id,
                "student_id": a.student_id,
                "type": a.type,
                "subject": a.subject,
                "score": a.score,
                "max_score": a.max_score,
                "timestamp": a.timestamp.isoformat()
            } for a in assessments]
        except Exception as e:
            logger.error(f"Error getting assessments: {str(e)}")
            return []
        finally:
            session.close()
    
    # ==================== PERFORMANCE OPERATIONS ====================
    
    def update_performance_record(self, student_id: str, data: Dict[str, Any]) -> Dict:
        """Add or update performance record for a student."""
        if self.use_fallback:
            performance_records_fallback[student_id] = {
                "student_id": student_id,
                "integrity_score": data.get("integrity_score", 0.0),
                "grit_level": data.get("grit_level", 0.0),
                "status": data.get("status", "Active"),
                "updated_at": datetime.now().isoformat()
            }
            return performance_records_fallback[student_id]
        
        session = self.get_session()
        try:
            record = session.execute(
                select(PerformanceRecord).where(PerformanceRecord.student_id == student_id)
            ).scalars().first()
            
            if not record:
                record = PerformanceRecord(
                    id=str(uuid.uuid4()),
                    student_id=student_id
                )
            
            # Update fields
            for key, value in data.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            
            session.add(record)
            session.commit()
            
            return {
                "student_id": record.student_id,
                "integrity_score": record.integrity_score,
                "grit_level": record.grit_level,
                "status": record.status,
                "updated_at": record.updated_at.isoformat()
            }
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating performance record: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_performance_record(self, student_id: str) -> Optional[Dict]:
        """Get performance record for a student."""
        if self.use_fallback:
            return performance_records_fallback.get(student_id)
        
        session = self.get_session()
        try:
            record = session.execute(
                select(PerformanceRecord).where(PerformanceRecord.student_id == student_id)
            ).scalars().first()
            
            if record:
                return {
                    "student_id": record.student_id,
                    "integrity_score": record.integrity_score,
                    "grit_level": record.grit_level,
                    "status": record.status,
                    "strengths": record.strengths,
                    "weaknesses": record.weaknesses,
                    "updated_at": record.updated_at.isoformat()
                }
            return None
        except Exception as e:
            logger.error(f"Error getting performance record: {str(e)}")
            return None
        finally:
            session.close()
    
    # ==================== ACTION LOGGING ====================
    
    def log_action(self, student_id: str, action: str, metadata: Optional[Dict] = None) -> Dict:
        """Log a student action for audit trail."""
        action_id = str(uuid.uuid4())
        
        if self.use_fallback:
            # Fallback: just log to console
            logger.info(f"Action: {action} by {student_id}")
            return {"id": action_id, "action": action, "student_id": student_id}
        
        session = self.get_session()
        try:
            log_entry = ActionLog(
                id=action_id,
                student_id=student_id,
                action=action,
                extra_data=metadata or {}
            )
            session.add(log_entry)
            session.commit()
            return {
                "id": log_entry.id,
                "action": log_entry.action,
                "student_id": log_entry.student_id,
                "timestamp": log_entry.timestamp.isoformat()
            }
        except Exception as e:
            session.rollback()
            logger.error(f"Error logging action: {str(e)}")
            return {}
        finally:
            session.close()


# Global datastore instance
datastore = DatastoreManager()


# Legacy interface functions (for backward compatibility)
def add_student(student_id: str, name: str, email: str):
    return datastore.add_student(student_id, name, email)


def get_student(student_id: str):
    return datastore.get_student(student_id)


def add_draft(student_id: str, text: str):
    draft_id = str(uuid.uuid4())
    return datastore.add_draft(student_id, draft_id, text)


def add_assessment(student_id: str, type: str, subject: str, score: float):
    return datastore.add_assessment(student_id, type, subject, score)


# ==================== COMPATIBILITY EXPORTS ====================
# For backward compatibility with existing routers that expect dict-based access
# These return data from the database or fallback

class StudentDictWrapper:
    """Wrapper to make datastore compatible with dict-like access for students."""
    def __contains__(self, key):
        return datastore.get_student(key) is not None
    
    def __setitem__(self, key, value):
        if isinstance(value, dict):
            datastore.add_student(key, value.get('name', ''), value.get('email', ''))
    
    def __getitem__(self, key):
        result = datastore.get_student(key)
        return result if result else {}
    
    def __delitem__(self, key):
        # Mark student as deleted instead of actually deleting
        pass

class AssessmentListWrapper:
    """Wrapper to make assessments compatible with list-like access."""
    def __init__(self):
        self.data = assessments_fallback
    
    def append(self, item):
        if datastore and datastore.use_fallback:
            self.data.append(item)
    
    def __iter__(self):
        return iter(self.data)
    
    def __getitem__(self, idx):
        return self.data[idx]
    
    def __setitem__(self, idx, value):
        self.data[idx] = value

# Export wrapper instances for backward compatibility
students = StudentDictWrapper()
performance_records = performance_records_fallback
assessments = AssessmentListWrapper()
drafts = drafts_fallback
