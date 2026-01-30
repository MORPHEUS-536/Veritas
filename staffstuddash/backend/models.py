from pydantic import BaseModel
from typing import List
from datetime import datetime

# Represents a single draft submitted by a student
class Draft(BaseModel):
    text: str                     # Student's submitted content
    timestamp: datetime           # When the draft was submitted

# Represents a student
class Student(BaseModel):
    id: str
    name: str

class ConceptModule(BaseModel):
    concept_id: str
    concept_name: str
    subject: str                  # Physics | Math | Biology
    difficulty_level: int         # 1-5
    attempt_count: int

class ProgressVisuals(BaseModel):
    learning_progress_score: float # 0-100
    semantic_change_score: float   # 0.0-1.0
    reasoning_continuity: str      # HIGH | MEDIUM | LOW

class IntegrityPanel(BaseModel):
    integrity_score: float         # 0.0-1.0
    sudden_jump_flag: bool         # True/False
    integrity_status_label: str    # CONSISTENT | NEEDS_REVIEW

class StagnationTracker(BaseModel):
    stagnation_duration_minutes: float
    repeat_attempt_count: int
    no_progress_flag: bool
    learning_state: str            # PROGRESSING | PLATEAU | STALLED
    dropout_risk_level: str        # LOW | MEDIUM | HIGH

# Stores all computed analytics for a student
class PerformanceRecord(BaseModel):
    student_id: str
    strengths: List[str] = []     # Top skills (e.g., ["Critical Thinking", "Algebra"])
    weaknesses: List[str] = []    # Areas for improvement
    subject_scores: dict = {}     # Detailed scores per subject/topic from metadata
    
    # Legacy flat fields (kept for backward compatibility if needed, or mapped to new structs)
    integrity_score: float        
    grit_level: float             
    status: str                   
    flags: bool                   
    recap_required: bool          
    
    # New Nested Telemetry
    concept: ConceptModule = None
    progress: ProgressVisuals = None
    integrity: IntegrityPanel = None
    stagnation: StagnationTracker = None

# Represents a raw score input (Test/Homework)
class AssessmentLog(BaseModel):
    student_id: str
    type: str                     # e.g., "exam", "quiz", "homework"
    subject: str                  # e.g., "Math", "Physics"
    topic: str = "General"        # e.g., "Calculus", "Thermodynamics"
    score: float                  # The obtained score
    max_score: float = 100.0      # Maximum possible score
    timestamp: datetime = datetime.now()
