"""
Feature Extraction Layer
Transforms raw events into interpretable signals across all seven categories.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from models import (
    LearningEvent, EventType, AttemptHistory, ComprehensiveFeatureSet,
    LearningProgressSignals, StagnationSignals, IntegritySignals,
    AIReasoningSignals, CompetitionAwareSignals, BehavioralDisengagementSignals,
    InterventionResponseSignals, ChangeType, LearningState
)
from event_collector import EventCollector
import statistics


class FeatureExtractor:
    """
    Extracts interpretable features from raw events.
    Produces seven categories of signals for dropout detection.
    """
    
    def __init__(self, event_collector: EventCollector):
        self.collector = event_collector
    
    # ====================
    # 1️⃣ LEARNING PROGRESS SIGNALS
    # ====================
    
    def extract_learning_progress_signals(
        self,
        student_id: str,
        question_id: str
    ) -> LearningProgressSignals:
        """
        Extract signals about student's learning progress.
        Answers: "Is the student actually moving forward?"
        """
        history = self.collector.build_attempt_history(student_id, question_id)
        attempt_count = history.attempt_count
        
        if attempt_count == 0:
            return LearningProgressSignals(
                attempt_count=0,
                attempt_frequency=0.0,
                time_spent_per_attempt=[],
                improvement_score=0.0
            )
        
        # Calculate time-based metrics
        events = self.collector.get_events_for_student_question(student_id, question_id)
        submit_events = [e for e in events if e.event_type == EventType.QUESTION_SUBMIT]
        
        time_spent_list = [
            e.data.get("time_spent_seconds", 0.0)
            for e in submit_events
        ]
        
        # Calculate attempt frequency (attempts per minute)
        if len(submit_events) >= 2:
            first_submit = submit_events[0].timestamp
            last_submit = submit_events[-1].timestamp
            time_diff = (last_submit - first_submit).total_seconds() / 60.0
            attempt_frequency = attempt_count / max(time_diff, 1.0)
        else:
            attempt_frequency = 0.0
        
        # Calculate improvement score (based on correctness progression)
        correctness_progression = [
            float(attempt.get("is_correct", False))
            for attempt in history.attempts
        ]
        
        if len(correctness_progression) > 1:
            # Score improvement: did they get more correct over attempts?
            early_avg = statistics.mean(correctness_progression[:len(correctness_progression)//2])
            late_avg = statistics.mean(correctness_progression[len(correctness_progression)//2:])
            improvement_score = max(0, (late_avg - early_avg)) * 100
        else:
            improvement_score = 100 if (correctness_progression and correctness_progression[0]) else 0
        
        # Classify change types between attempts
        change_types = self._classify_change_types(history)
        
        # Semantic change score
        semantic_score = self._calculate_semantic_change_score(history, change_types)
        
        # Determine learning state
        learning_state = self._determine_learning_state(
            improvement_score,
            attempt_count,
            change_types
        )
        
        # Set no_progress_flag if no semantic improvement
        no_progress_flag = (semantic_score < 30 and attempt_count >= 3)
        
        return LearningProgressSignals(
            attempt_count=attempt_count,
            attempt_frequency=attempt_frequency,
            time_spent_per_attempt=time_spent_list,
            improvement_score=min(100, max(0, improvement_score)),
            change_type=change_types,
            semantic_change_score=min(100, max(0, semantic_score)),
            no_progress_flag=no_progress_flag,
            learning_state=learning_state
        )
    
    def _classify_change_types(self, history: AttemptHistory) -> List[ChangeType]:
        """Classify changes between consecutive attempts."""
        if len(history.attempts) <= 1:
            return []
        
        change_types = []
        for i in range(1, len(history.attempts)):
            prev_answer = history.attempts[i-1]["answer"]
            curr_answer = history.attempts[i]["answer"]
            
            # Simple heuristic: check if it's just formatting vs logic change
            if self._is_superficial_change(prev_answer, curr_answer):
                change_types.append(ChangeType.SUPERFICIAL)
            elif prev_answer != curr_answer and history.attempts[i].get("is_correct"):
                change_types.append(ChangeType.CORRECTIVE)
            else:
                change_types.append(ChangeType.STRUCTURAL)
        
        return change_types
    
    def _is_superficial_change(self, text1: str, text2: str) -> bool:
        """Determine if change is superficial (formatting) or semantic."""
        # Simple heuristic: remove whitespace and compare
        cleaned1 = "".join(text1.split()).lower()
        cleaned2 = "".join(text2.split()).lower()
        return cleaned1 == cleaned2
    
    def _calculate_semantic_change_score(
        self,
        history: AttemptHistory,
        change_types: List[ChangeType]
    ) -> float:
        """Calculate how much semantic (meaningful) changes occurred."""
        if not change_types:
            return 0.0
        
        # Score based on CORRECTIVE and STRUCTURAL changes
        semantic_changes = sum(
            1 for ct in change_types
            if ct in [ChangeType.CORRECTIVE, ChangeType.STRUCTURAL]
        )
        return (semantic_changes / len(change_types)) * 100
    
    def _determine_learning_state(
        self,
        improvement_score: float,
        attempt_count: int,
        change_types: List[ChangeType]
    ) -> LearningState:
        """Determine current learning state."""
        if improvement_score > 60 and attempt_count <= 3:
            return LearningState.PROGRESSING
        elif attempt_count > 5 and improvement_score < 30:
            return LearningState.STALLED
        else:
            return LearningState.PLATEAU
    
    # ====================
    # 2️⃣ STAGNATION SIGNALS
    # ====================
    
    def extract_stagnation_signals(
        self,
        student_id: str,
        question_id: str
    ) -> StagnationSignals:
        """
        Extract signals about stagnation/being stuck.
        Answers: "Is the student stuck for too long?"
        """
        events = self.collector.get_events_for_student_question(student_id, question_id)
        history = self.collector.build_attempt_history(student_id, question_id)
        
        if not events:
            return StagnationSignals(
                stagnation_duration_minutes=0.0,
                repeat_attempt_count=0,
                concept_revisit_frequency=0.0
            )
        
        # Calculate stagnation duration
        submit_events = [e for e in events if e.event_type == EventType.QUESTION_SUBMIT]
        if len(submit_events) > 1:
            first_submit = submit_events[0].timestamp
            last_submit = submit_events[-1].timestamp
            stagnation_duration = (last_submit - first_submit).total_seconds() / 60.0
        else:
            stagnation_duration = 0.0
        
        # Repeat attempt count
        repeat_attempt_count = history.attempt_count
        
        # Concept revisit frequency (how many times same question revisited in session)
        concept_revisit_freq = max(0, repeat_attempt_count - 1)
        
        # Improvement tracking
        correctness_progression = [
            float(attempt.get("is_correct", False))
            for attempt in history.attempts
        ]
        
        recent_score = correctness_progression[-1] if correctness_progression else 0
        improvement = sum(1 for c in correctness_progression if c > 0) / max(1, len(correctness_progression))
        
        # Stagnation threshold: 3+ attempts, 15+ minutes, no improvement
        is_stalled = (
            repeat_attempt_count >= 3
            and stagnation_duration >= 15
            and improvement < 0.5
        )
        
        # Severity calculation
        severity = min(100, (repeat_attempt_count * 20) + (stagnation_duration / 5))
        
        return StagnationSignals(
            stagnation_duration_minutes=stagnation_duration,
            repeat_attempt_count=repeat_attempt_count,
            concept_revisit_frequency=concept_revisit_freq,
            is_stalled=is_stalled,
            stagnation_severity=severity
        )
    
    # ====================
    # 3️⃣ INTEGRITY & AUTHENTICITY SIGNALS
    # ====================
    
    def extract_integrity_signals(
        self,
        student_id: str,
        question_id: str
    ) -> IntegritySignals:
        """
        Extract signals about learning authenticity.
        Answers: "Does this learning look consistent and authentic?"
        """
        events = self.collector.get_events_for_student_question(student_id, question_id)
        history = self.collector.build_attempt_history(student_id, question_id)
        
        if not history.attempts:
            return IntegritySignals(
                integrity_score=100.0,
                reasoning_continuity="HIGH",
                sudden_jump_flag=False,
                external_assistance_likelihood=0.0
            )
        
        # Check for sudden jumps in correctness
        correctness_progression = [
            float(attempt.get("is_correct", False))
            for attempt in history.attempts
        ]
        
        sudden_jump = False
        if len(correctness_progression) >= 2:
            for i in range(1, len(correctness_progression)):
                if correctness_progression[i] > correctness_progression[i-1] + 0.5:
                    sudden_jump = True
                    break
        
        # Reasoning continuity based on answer length and structure
        answer_lengths = [len(a.get("answer", "")) for a in history.attempts]
        if len(answer_lengths) > 1:
            length_variance = statistics.variance(answer_lengths) if len(answer_lengths) > 1 else 0
            avg_length = statistics.mean(answer_lengths)
            
            # High variance + sudden jump = suspicious
            if length_variance > avg_length * 2 and sudden_jump:
                continuity = "LOW"
                external_likelihood = 0.6
            elif length_variance > avg_length:
                continuity = "MEDIUM"
                external_likelihood = 0.3
            else:
                continuity = "HIGH"
                external_likelihood = 0.1
        else:
            continuity = "HIGH"
            external_likelihood = 0.1
        
        # Base integrity score
        base_score = 100.0
        if sudden_jump:
            base_score -= 20
        if external_likelihood > 0.5:
            base_score -= 15
        
        integrity_score = max(0, base_score)
        
        return IntegritySignals(
            integrity_score=integrity_score,
            reasoning_continuity=continuity,
            sudden_jump_flag=sudden_jump,
            external_assistance_likelihood=external_likelihood
        )
    
    # ====================
    # 4️⃣ AI REASONING SIGNALS (placeholder)
    # ====================
    
    def extract_ai_reasoning_signals(
        self,
        student_id: str,
        question_id: str
    ) -> AIReasoningSignals:
        """
        Placeholder for AI-based cognitive analysis.
        This will be populated by the LLM Analysis Layer.
        """
        return AIReasoningSignals(
            conceptual_gap_description="Pending LLM analysis",
            learning_summary="Pending LLM analysis",
            llm_confidence_estimate=0.0
        )
    
    # ====================
    # 5️⃣ COMPETITION-AWARE SIGNALS
    # ====================
    
    def extract_competition_aware_signals(
        self,
        student_id: str,
        question_id: str,
        latest_mock_rank: Optional[int] = None,
        previous_mock_rank: Optional[int] = None
    ) -> CompetitionAwareSignals:
        """
        Extract signals related to competition pressure (India context).
        Answers: "Is competition causing disengagement?"
        """
        rank_delta = None
        if latest_mock_rank and previous_mock_rank:
            rank_delta = latest_mock_rank - previous_mock_rank  # Negative = improved, Positive = worsened
        
        # Relative progress index based on attempt history
        history = self.collector.build_attempt_history(student_id, question_id)
        correctness = [float(a.get("is_correct")) for a in history.attempts]
        
        if correctness:
            relative_progress = (sum(correctness) / len(correctness)) * 100
        else:
            relative_progress = 0.0
        
        # Competition pressure flag
        pressure_flag = False
        if rank_delta and rank_delta > 0:  # Rank worsened
            pressure_flag = True
        if relative_progress < 30:
            pressure_flag = True
        
        return CompetitionAwareSignals(
            latest_mock_rank=latest_mock_rank,
            previous_mock_rank=previous_mock_rank,
            rank_delta=rank_delta,
            relative_progress_index=relative_progress,
            competition_pressure_flag=pressure_flag
        )
    
    # ====================
    # 6️⃣ BEHAVIORAL DISENGAGEMENT SIGNALS
    # ====================
    
    def extract_behavioral_disengagement_signals(
        self,
        student_id: str,
        question_id: str
    ) -> BehavioralDisengagementSignals:
        """
        Extract signals about effort and engagement over time.
        Answers: "Is effort reducing over time?"
        """
        events = self.collector.get_events_for_student_question(student_id, question_id)
        submit_events = [e for e in events if e.event_type == EventType.QUESTION_SUBMIT]
        
        # Calculate attempt gaps
        attempt_gaps = []
        for i in range(1, len(submit_events)):
            gap = (submit_events[i].timestamp - submit_events[i-1].timestamp).total_seconds()
            attempt_gaps.append(gap)
        
        # Daily attempt count (simplified: assume session boundaries)
        daily_attempts = [len(submit_events)]  # Single session
        
        # Consistency score (lower gaps = more consistent)
        if attempt_gaps:
            avg_gap = statistics.mean(attempt_gaps)
            consistency = max(0, 100 - (avg_gap / 60))  # Normalize to ~1 minute gap
        else:
            consistency = 100.0
        
        # Average gap increasing (gaps getting longer = disengagement)
        avg_gap_increasing = False
        if len(attempt_gaps) > 1:
            first_half_gap = statistics.mean(attempt_gaps[:len(attempt_gaps)//2])
            second_half_gap = statistics.mean(attempt_gaps[len(attempt_gaps)//2:])
            avg_gap_increasing = second_half_gap > first_half_gap * 1.2  # 20% increase threshold
        
        return BehavioralDisengagementSignals(
            attempt_gap_time=attempt_gaps,
            daily_attempt_count=daily_attempts,
            consistency_score=min(100, max(0, consistency)),
            average_gap_increasing=avg_gap_increasing
        )
    
    # ====================
    # 7️⃣ INTERVENTION RESPONSE SIGNALS
    # ====================
    
    def extract_intervention_response_signals(
        self,
        student_id: str,
        question_id: str
    ) -> InterventionResponseSignals:
        """
        Extract signals about response to interventions.
        Answers: "Did intervention help?"
        """
        # Placeholder: would track interventions and post-intervention progress
        return InterventionResponseSignals(
            intervention_triggered=False,
            intervention_type=None,
            intervention_timestamp=None,
            post_intervention_progress=0.0,
            recovery_score=0.0,
            intervention_success_flag=False
        )
    
    # ====================
    # COMPREHENSIVE FEATURE EXTRACTION
    # ====================
    
    def extract_comprehensive_features(
        self,
        student_id: str,
        question_id: str,
        latest_mock_rank: Optional[int] = None,
        previous_mock_rank: Optional[int] = None
    ) -> ComprehensiveFeatureSet:
        """
        Extract all seven signal categories for a student-question pair.
        This is the final output of the Feature Extraction Layer.
        """
        return ComprehensiveFeatureSet(
            student_id=student_id,
            question_id=question_id,
            timestamp=datetime.now(),
            learning_progress=self.extract_learning_progress_signals(student_id, question_id),
            stagnation=self.extract_stagnation_signals(student_id, question_id),
            integrity=self.extract_integrity_signals(student_id, question_id),
            ai_reasoning=self.extract_ai_reasoning_signals(student_id, question_id),
            competition_aware=self.extract_competition_aware_signals(
                student_id, question_id, latest_mock_rank, previous_mock_rank
            ),
            behavioral_disengagement=self.extract_behavioral_disengagement_signals(student_id, question_id),
            intervention_response=self.extract_intervention_response_signals(student_id, question_id)
        )
