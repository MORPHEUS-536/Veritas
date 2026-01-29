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

# Stores all computed analytics for a student
class PerformanceRecord(BaseModel):
    student_id: str
    strengths: List[str] = []     # Top skills (e.g., ["Critical Thinking", "Algebra"])
    weaknesses: List[str] = []    # Areas for improvement
    subject_scores: dict = {}     # Detailed scores per subject/topic from metadata
    integrity_score: float        # How genuine the thinking is
    lmi_score: float              # Learning Momentum Index
    dropout_risk: str             # incapable | copy | no_interest | safe
    flagged: bool                 # Whether instructor attention is needed
    recap_required: bool          # Whether system should suggest recap

# Represents a raw score input (Test/Homework)
class AssessmentLog(BaseModel):
    student_id: str
    type: str                     # e.g., "exam", "quiz", "homework"
    subject: str                  # e.g., "Math", "Physics"
    topic: str = "General"        # e.g., "Calculus", "Thermodynamics"
    score: float                  # The obtained score
    max_score: float = 100.0      # Maximum possible score
    timestamp: datetime = datetime.now()
