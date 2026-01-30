"""
Data models for the Dropout Detection System.
Defines immutable event structures and feature representations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Literal
from enum import Enum
import uuid


class EventType(Enum):
    """Types of learning events that can be tracked."""
    QUESTION_START = "question_start"
    QUESTION_SUBMIT = "question_submit"
    ANSWER_REVISION = "answer_revision"
    NAVIGATION = "navigation"
    FOCUS_BLUR = "focus_blur"
    FOCUS_FOCUS = "focus_focus"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    HINT_REQUEST = "hint_request"


class ChangeType(Enum):
    """Classification of the type of change between attempts."""
    SUPERFICIAL = "SUPERFICIAL"  # Syntax/formatting only
    STRUCTURAL = "STRUCTURAL"    # Logic restructuring
    CORRECTIVE = "CORRECTIVE"    # Error correction


class LearningState(Enum):
    """State of learner's progress."""
    PROGRESSING = "PROGRESSING"
    PLATEAU = "PLATEAU"
    STALLED = "STALLED"


class DropoutType(Enum):
    """Types of dropout classification."""
    COGNITIVE = "COGNITIVE"
    BEHAVIORAL = "BEHAVIORAL"
    ENGAGEMENT = "ENGAGEMENT"
    SILENT = "SILENT"
    NO_DROPOUT = "NO_DROPOUT"


@dataclass(frozen=True)  # Immutable
class LearningEvent:
    """
    Immutable representation of a learning event.
    Events are time-ordered and cannot be modified.
    """
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = field(default=EventType.QUESTION_START)
    student_id: str = ""
    question_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate immutability constraints."""
        if not self.student_id or not self.question_id:
            raise ValueError("student_id and question_id are required")


@dataclass
class AttemptHistory:
    """Tracks multiple attempts on a single question."""
    question_id: str
    student_id: str
    attempts: List[Dict] = field(default_factory=list)
    
    def add_attempt(self, answer: str, timestamp: datetime, is_correct: bool = False):
        """Add a new attempt to the history."""
        self.attempts.append({
            "answer": answer,
            "timestamp": timestamp,
            "is_correct": is_correct,
            "attempt_number": len(self.attempts) + 1
        })
    
    @property
    def attempt_count(self) -> int:
        return len(self.attempts)
    
    @property
    def correct_on_first_attempt(self) -> bool:
        return len(self.attempts) == 1 and self.attempts[0].get("is_correct", False)


# ====================
# SIGNAL DEFINITIONS
# ====================

@dataclass
class LearningProgressSignals:
    """1️⃣ LEARNING PROGRESS SIGNALS (PRIMARY)"""
    attempt_count: int
    attempt_frequency: float  # attempts per minute
    time_spent_per_attempt: List[float]  # in seconds
    improvement_score: float  # 0-100
    change_type: List[ChangeType] = field(default_factory=list)
    semantic_change_score: float = 0.0  # 0-100
    no_progress_flag: bool = False
    learning_state: LearningState = LearningState.PROGRESSING


@dataclass
class StagnationSignals:
    """2️⃣ STAGNATION SIGNALS (MOST IMPORTANT)"""
    stagnation_duration_minutes: float
    repeat_attempt_count: int
    concept_revisit_frequency: float  # times revisited
    is_stalled: bool = False
    stagnation_severity: float = 0.0  # 0-100


@dataclass
class IntegritySignals:
    """3️⃣ INTEGRITY & AUTHENTICITY SIGNALS (SUPPORTING)"""
    integrity_score: float  # 0-100
    reasoning_continuity: Literal["HIGH", "MEDIUM", "LOW"]
    sudden_jump_flag: bool
    external_assistance_likelihood: float  # 0-1


@dataclass
class AIReasoningSignals:
    """4️⃣ AI REASONING & EXPLANATION SIGNALS (INTERPRETIVE)"""
    conceptual_gap_description: str
    learning_summary: str
    llm_confidence_estimate: float  # 0-1
    misconception_patterns: List[str] = field(default_factory=list)
    confidence_vs_correctness_gap: float = 0.0


@dataclass
class CompetitionAwareSignals:
    """5️⃣ COMPETITION-AWARE SIGNALS (NOVEL FACTOR - India context)"""
    latest_mock_rank: Optional[int] = None
    previous_mock_rank: Optional[int] = None
    rank_delta: Optional[int] = None
    relative_progress_index: float = 0.0  # 0-100
    competition_pressure_flag: bool = False


@dataclass
class BehavioralDisengagementSignals:
    """6️⃣ BEHAVIORAL DISENGAGEMENT SIGNALS"""
    attempt_gap_time: List[float] = field(default_factory=list)  # seconds between attempts
    daily_attempt_count: List[int] = field(default_factory=list)
    consistency_score: float = 0.0  # 0-100
    average_gap_increasing: bool = False


@dataclass
class InterventionResponseSignals:
    """7️⃣ INTERVENTION RESPONSE SIGNALS (POST-DETECTION)"""
    intervention_triggered: bool = False
    intervention_type: Optional[str] = None
    intervention_timestamp: Optional[datetime] = None
    post_intervention_progress: float = 0.0  # 0-100
    recovery_score: float = 0.0  # 0-100
    intervention_success_flag: bool = False


@dataclass
class ComprehensiveFeatureSet:
    """
    Aggregates all seven signal categories into one comprehensive feature set.
    This is the output of the Feature Extraction Layer.
    """
    student_id: str
    question_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Signal Categories
    learning_progress: LearningProgressSignals = field(default_factory=lambda: LearningProgressSignals(
        attempt_count=0, attempt_frequency=0.0, time_spent_per_attempt=[], improvement_score=0.0))
    stagnation: StagnationSignals = field(default_factory=lambda: StagnationSignals(
        stagnation_duration_minutes=0.0, repeat_attempt_count=0, concept_revisit_frequency=0.0))
    integrity: IntegritySignals = field(default_factory=lambda: IntegritySignals(
        integrity_score=100.0, reasoning_continuity="HIGH", sudden_jump_flag=False, 
        external_assistance_likelihood=0.0))
    ai_reasoning: AIReasoningSignals = field(default_factory=lambda: AIReasoningSignals(
        conceptual_gap_description="", learning_summary="", llm_confidence_estimate=0.0))
    competition_aware: CompetitionAwareSignals = field(default_factory=CompetitionAwareSignals)
    behavioral_disengagement: BehavioralDisengagementSignals = field(default_factory=BehavioralDisengagementSignals)
    intervention_response: InterventionResponseSignals = field(default_factory=InterventionResponseSignals)


# ====================
# SCORING STRUCTURES
# ====================

@dataclass
class LearningMomentumIndex:
    """
    LMI measures directional improvement of thinking quality across attempts.
    Scale: 0-100
    - LMI > 70 → Healthy learning
    - LMI 40-70 → At-risk
    - LMI < 40 → Dropout trajectory
    """
    lmi_score: float  # 0-100
    momentum_direction: Literal["ACCELERATING", "STABLE", "DECELERATING"]
    decay_rate: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DropoutRiskScore:
    """
    DRS aggregates all signals into a single actionable score.
    Scale: 0-1
    """
    drs_score: float  # 0-1
    confidence: float  # 0-1
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    primary_risk_factors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DropoutClassification:
    """
    Final classification result combining rule + score hybrid logic.
    """
    is_dropout: bool
    dropout_types: List[DropoutType] = field(default_factory=list)
    primary_reason: str = ""
    lmi_score: float = 0.0
    drs_score: float = 0.0
    confidence: float = 0.0
    recommendation: str = ""
    primary_risk_factors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        if not self.is_dropout:
            return f"✓ No Dropout (Confidence: {self.confidence:.2%})"
        types_str = ", ".join([dt.value for dt in self.dropout_types])
        return f"⚠ DROPOUT DETECTED: {types_str}\n  Reason: {self.primary_reason}\n  LMI: {self.lmi_score:.1f} | DRS: {self.drs_score:.2f}"
