"""
Event Collection Layer
Captures raw, timestamped learning events in immutable, time-ordered fashion.
"""

from datetime import datetime
from typing import List, Optional, Dict
from models import LearningEvent, EventType, AttemptHistory
from collections import defaultdict


class EventCollector:
    """
    Manages collection of immutable learning events.
    Ensures time-ordering and immutability constraints.
    """
    
    def __init__(self):
        self.events: List[LearningEvent] = []
        self.event_index: Dict[str, List[LearningEvent]] = defaultdict(list)
        self._last_timestamp: Optional[datetime] = None
    
    def record_event(
        self,
        event_type: EventType,
        student_id: str,
        question_id: str,
        data: Optional[Dict] = None
    ) -> LearningEvent:
        """
        Record a new immutable event.
        Enforces time-ordering: each event must have timestamp >= previous event.
        
        Args:
            event_type: Type of learning event
            student_id: Student identifier
            question_id: Question identifier
            data: Event-specific data payload
        
        Returns:
            The recorded LearningEvent (immutable)
        """
        timestamp = datetime.now()
        
        # Enforce time-ordering
        if self._last_timestamp and timestamp < self._last_timestamp:
            raise ValueError(f"Event timestamp {timestamp} is before last event {self._last_timestamp}")
        
        self._last_timestamp = timestamp
        
        # Create immutable event
        event = LearningEvent(
            event_type=event_type,
            student_id=student_id,
            question_id=question_id,
            timestamp=timestamp,
            data=data or {}
        )
        
        # Append to ordered list
        self.events.append(event)
        
        # Index by (student_id, question_id) for quick lookup
        key = f"{student_id}:{question_id}"
        self.event_index[key].append(event)
        
        return event
    
    def record_question_start(
        self,
        student_id: str,
        question_id: str,
        question_content: Optional[str] = None
    ) -> LearningEvent:
        """Record the moment a student starts a question."""
        return self.record_event(
            EventType.QUESTION_START,
            student_id,
            question_id,
            {"question_content": question_content}
        )
    
    def record_question_submit(
        self,
        student_id: str,
        question_id: str,
        answer: str,
        is_correct: bool = False,
        time_spent_seconds: float = 0.0
    ) -> LearningEvent:
        """Record answer submission with correctness and time spent."""
        return self.record_event(
            EventType.QUESTION_SUBMIT,
            student_id,
            question_id,
            {
                "answer": answer,
                "is_correct": is_correct,
                "time_spent_seconds": time_spent_seconds
            }
        )
    
    def record_answer_revision(
        self,
        student_id: str,
        question_id: str,
        original_answer: str,
        revised_answer: str,
        revision_reason: Optional[str] = None
    ) -> LearningEvent:
        """Record when student revises their answer."""
        return self.record_event(
            EventType.ANSWER_REVISION,
            student_id,
            question_id,
            {
                "original_answer": original_answer,
                "revised_answer": revised_answer,
                "revision_reason": revision_reason
            }
        )
    
    def record_navigation(
        self,
        student_id: str,
        question_id: str,
        nav_type: str,  # "next", "back", "skip"
        destination_question_id: Optional[str] = None
    ) -> LearningEvent:
        """Record navigation events (next, back, skip)."""
        return self.record_event(
            EventType.NAVIGATION,
            student_id,
            question_id,
            {
                "nav_type": nav_type,
                "destination_question_id": destination_question_id
            }
        )
    
    def record_focus_loss(
        self,
        student_id: str,
        question_id: str,
        idle_duration_seconds: float
    ) -> LearningEvent:
        """Record when student loses focus on the question."""
        return self.record_event(
            EventType.FOCUS_BLUR,
            student_id,
            question_id,
            {"idle_duration_seconds": idle_duration_seconds}
        )
    
    def record_focus_gain(
        self,
        student_id: str,
        question_id: str
    ) -> LearningEvent:
        """Record when student refocuses on the question."""
        return self.record_event(
            EventType.FOCUS_FOCUS,
            student_id,
            question_id,
            {}
        )
    
    def record_hint_request(
        self,
        student_id: str,
        question_id: str,
        hint_level: int = 1
    ) -> LearningEvent:
        """Record when student requests a hint."""
        return self.record_event(
            EventType.HINT_REQUEST,
            student_id,
            question_id,
            {"hint_level": hint_level}
        )
    
    def record_session_start(
        self,
        student_id: str,
        question_id: str = "session"
    ) -> LearningEvent:
        """Record start of learning session."""
        return self.record_event(
            EventType.SESSION_START,
            student_id,
            question_id,
            {}
        )
    
    def record_session_end(
        self,
        student_id: str,
        question_id: str = "session"
    ) -> LearningEvent:
        """Record end of learning session."""
        return self.record_event(
            EventType.SESSION_END,
            student_id,
            question_id,
            {}
        )
    
    def get_events_for_student_question(
        self,
        student_id: str,
        question_id: str
    ) -> List[LearningEvent]:
        """Retrieve all time-ordered events for a student-question pair."""
        key = f"{student_id}:{question_id}"
        return self.event_index.get(key, [])
    
    def get_events_for_student(self, student_id: str) -> List[LearningEvent]:
        """Retrieve all events for a specific student (time-ordered)."""
        return [e for e in self.events if e.student_id == student_id]
    
    def get_events_for_question(self, question_id: str) -> List[LearningEvent]:
        """Retrieve all events for a specific question."""
        return [e for e in self.events if e.question_id == question_id]
    
    def get_events_by_type(self, event_type: EventType) -> List[LearningEvent]:
        """Retrieve all events of a specific type."""
        return [e for e in self.events if e.event_type == event_type]
    
    def build_attempt_history(
        self,
        student_id: str,
        question_id: str
    ) -> AttemptHistory:
        """
        Construct attempt history from QUESTION_SUBMIT events.
        Maintains chronological order.
        """
        events = self.get_events_for_student_question(student_id, question_id)
        submit_events = [e for e in events if e.event_type == EventType.QUESTION_SUBMIT]
        
        history = AttemptHistory(question_id, student_id)
        for event in submit_events:
            history.add_attempt(
                answer=event.data.get("answer", ""),
                timestamp=event.timestamp,
                is_correct=event.data.get("is_correct", False)
            )
        return history
    
    def get_all_events(self) -> List[LearningEvent]:
        """Get all recorded events in time order."""
        return list(self.events)
    
    def event_count(self) -> int:
        """Total number of recorded events."""
        return len(self.events)
