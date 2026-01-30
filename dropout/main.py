"""
Main Orchestrator & Views
Complete system integration with Teacher and Student views.
Implements ethical constraints: supportive, not judgmental.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

from models import (
    DropoutType, ComprehensiveFeatureSet, DropoutClassification,
    LearningEvent, EventType
)
from event_collector import EventCollector
from feature_extractor import FeatureExtractor
from llm_analyzer import LLMAnalyzer
from scoring import ScoringEngine, ThresholdManager
from dropout_classifier import DropoutDetectionPipeline, DropoutClassifier


class UserRole(Enum):
    """User roles for view access."""
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"
    ADMIN = "ADMIN"


# ====================
# STUDENT VIEW
# ====================

class StudentView:
    """
    Student-facing view of their learning progress.
    Never shows "dropout" labels. Shows encouragement and adaptive support.
    """
    
    @staticmethod
    def generate_student_feedback(
        features: ComprehensiveFeatureSet,
        classification: DropoutClassification
    ) -> Dict:
        """
        Generate supportive, constructive feedback for student.
        Frames challenges as opportunities, not failures.
        """
        progress = features.learning_progress
        stagnation = features.stagnation
        ai_signals = features.ai_reasoning
        behavioral = features.behavioral_disengagement
        
        # Positive reinforcement
        strengths = []
        if progress.improvement_score > 60:
            strengths.append("You're showing solid improvement on this topic!")
        if progress.attempt_count > 1 and not stagnation.is_stalled:
            strengths.append("Great persistence - you're working through challenges.")
        if behavioral.consistency_score > 70:
            strengths.append("Your engagement is consistent and focused.")
        
        # Encouraging guidance
        growth_areas = []
        
        if stagnation.is_stalled:
            growth_areas.append({
                "area": "Try a Different Approach",
                "message": (
                    f"You've been on this problem for {stagnation.stagnation_duration_minutes:.0f} minutes. "
                    "Sometimes stepping back and viewing the problem differently helps. "
                    "Would you like a hint or to review the concept again?"
                ),
                "action": "OFFER_HINT"
            })
        
        if len(ai_signals.misconception_patterns) > 0:
            growth_areas.append({
                "area": "Concept Reinforcement",
                "message": (
                    f"Let's review: {ai_signals.conceptual_gap_description} "
                    "Understanding this deeply will help with similar problems."
                ),
                "action": "SUGGEST_RESOURCE"
            })
        
        if behavioral.average_gap_increasing:
            growth_areas.append({
                "area": "Stay Engaged",
                "message": (
                    "We notice you're taking longer between attempts. "
                    "Keep the momentum going - you're close to breakthrough!"
                ),
                "action": "MOTIVATIONAL_CHECK_IN"
            })
        
        if progress.semantic_change_score < 40 and progress.attempt_count >= 3:
            growth_areas.append({
                "area": "Deepen Your Understanding",
                "message": (
                    "Your answers are changing, but let's focus on understanding "
                    "the underlying concept better."
                ),
                "action": "CONCEPTUAL_SUPPORT"
            })
        
        # Adaptive difficulty suggestion
        if progress.learning_state.value == "PROGRESSING":
            difficulty_suggestion = "You're ready for a challenge! Try the next problem level."
        elif progress.learning_state.value == "PLATEAU":
            difficulty_suggestion = "Keep practicing at this level - you'll break through soon."
        else:
            difficulty_suggestion = "Let's review the fundamentals to build a stronger foundation."
        
        return {
            "timestamp": datetime.now().isoformat(),
            "role": "STUDENT",
            "strengths": strengths,
            "growth_areas": growth_areas,
            "next_steps": [g["message"] for g in growth_areas],
            "difficulty_suggestion": difficulty_suggestion,
            "encouragement": StudentView._generate_encouragement(features),
            "progress_summary": StudentView._generate_progress_summary(features)
        }
    
    @staticmethod
    def _generate_encouragement(features: ComprehensiveFeatureSet) -> str:
        """Generate personalized encouragement message."""
        messages = [
            "Every attempt teaches you something new.",
            "You're building problem-solving skills that will serve you well.",
            "Struggle is a sign of growth - you're on the right path.",
            "Your persistence is impressive. Keep it up!",
            "Learning isn't linear - setbacks are part of progress.",
            "You're developing mastery. This takes time and effort.",
            "Trust the process. Your efforts will compound.",
        ]
        
        # Select based on attempt count
        attempt_count = features.learning_progress.attempt_count
        return messages[attempt_count % len(messages)]
    
    @staticmethod
    def _generate_progress_summary(features: ComprehensiveFeatureSet) -> str:
        """Generate simple progress summary for student."""
        progress = features.learning_progress
        state_messages = {
            "PROGRESSING": "You're moving forward! 📈",
            "PLATEAU": "You're building strength. 💪",
            "STALLED": "Time for a new strategy. 🔄"
        }
        return state_messages.get(progress.learning_state.value, "Keep going! 🚀")


# ====================
# TEACHER VIEW
# ====================

class TeacherView:
    """
    Teacher/Admin-facing view with full dropout classification and analysis.
    Shows risk levels, patterns, and actionable interventions.
    """
    
    @staticmethod
    def generate_teacher_report(
        student_id: str,
        question_id: str,
        features: ComprehensiveFeatureSet,
        classification: DropoutClassification,
        intervention_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Generate comprehensive teacher report with full dropout analysis.
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "role": "TEACHER",
            "student_id": student_id,
            "question_id": question_id,
            
            # Dropout Status
            "dropout_status": TeacherView._format_dropout_status(classification),
            
            # Detailed Signals
            "signals": TeacherView._format_all_signals(features),
            
            # Scores and Trends
            "scores": TeacherView._format_scores(features, classification),
            
            # Primary Risk Factors
            "risk_factors": classification.primary_risk_factors,
            
            # Intervention Recommendation
            "intervention": TeacherView._format_intervention(classification),
            
            # Historical Context (if available)
            "intervention_history": intervention_history or [],
            
            # Visualization Data
            "visualizations": TeacherView._prepare_visualization_data(features, classification),
        }
    
    @staticmethod
    def _format_dropout_status(classification: DropoutClassification) -> Dict:
        """Format dropout detection status."""
        if not classification.is_dropout:
            return {
                "status": "NO_DROPOUT",
                "icon": "✓",
                "message": "Student appears to be on a healthy learning trajectory",
                "confidence": f"{classification.confidence:.0%}"
            }
        
        types_str = ", ".join([dt.value for dt in classification.dropout_types])
        
        return {
            "status": "DROPOUT_DETECTED",
            "icon": "⚠",
            "types": [dt.value for dt in classification.dropout_types],
            "types_string": types_str,
            "reason": classification.primary_reason,
            "confidence": f"{classification.confidence:.0%}",
            "lmi_score": f"{classification.lmi_score:.1f}/100",
            "drs_score": f"{classification.drs_score:.2f}/1.0"
        }
    
    @staticmethod
    def _format_all_signals(features: ComprehensiveFeatureSet) -> Dict:
        """Format all seven signal categories."""
        return {
            "1_learning_progress": {
                "attempt_count": features.learning_progress.attempt_count,
                "attempt_frequency": f"{features.learning_progress.attempt_frequency:.2f}/min",
                "improvement_score": f"{features.learning_progress.improvement_score:.1f}%",
                "semantic_change_score": f"{features.learning_progress.semantic_change_score:.1f}%",
                "change_types": [ct.value for ct in features.learning_progress.change_type],
                "learning_state": features.learning_progress.learning_state.value,
                "no_progress_flag": features.learning_progress.no_progress_flag
            },
            "2_stagnation": {
                "stagnation_duration_minutes": f"{features.stagnation.stagnation_duration_minutes:.1f}",
                "repeat_attempt_count": features.stagnation.repeat_attempt_count,
                "concept_revisit_frequency": f"{features.stagnation.concept_revisit_frequency:.1f}",
                "is_stalled": features.stagnation.is_stalled,
                "stagnation_severity": f"{features.stagnation.stagnation_severity:.1f}%"
            },
            "3_integrity": {
                "integrity_score": f"{features.integrity.integrity_score:.1f}%",
                "reasoning_continuity": features.integrity.reasoning_continuity,
                "sudden_jump_flag": features.integrity.sudden_jump_flag,
                "external_assistance_likelihood": f"{features.integrity.external_assistance_likelihood:.2f}"
            },
            "4_ai_reasoning": {
                "conceptual_gap": features.ai_reasoning.conceptual_gap_description,
                "learning_summary": features.ai_reasoning.learning_summary,
                "llm_confidence": f"{features.ai_reasoning.llm_confidence_estimate:.2f}",
                "misconceptions": features.ai_reasoning.misconception_patterns,
                "confidence_vs_correctness_gap": f"{features.ai_reasoning.confidence_vs_correctness_gap:.1f}"
            },
            "5_competition_aware": {
                "latest_mock_rank": features.competition_aware.latest_mock_rank,
                "previous_mock_rank": features.competition_aware.previous_mock_rank,
                "rank_delta": features.competition_aware.rank_delta,
                "relative_progress": f"{features.competition_aware.relative_progress_index:.1f}%",
                "competition_pressure_flag": features.competition_aware.competition_pressure_flag
            },
            "6_behavioral_disengagement": {
                "consistency_score": f"{features.behavioral_disengagement.consistency_score:.1f}%",
                "average_gap_increasing": features.behavioral_disengagement.average_gap_increasing,
                "attempt_gaps_seconds": [f"{g:.1f}" for g in features.behavioral_disengagement.attempt_gap_time],
                "daily_attempt_count": features.behavioral_disengagement.daily_attempt_count
            },
            "7_intervention_response": {
                "intervention_triggered": features.intervention_response.intervention_triggered,
                "intervention_type": features.intervention_response.intervention_type,
                "post_intervention_progress": f"{features.intervention_response.post_intervention_progress:.1f}%",
                "recovery_score": f"{features.intervention_response.recovery_score:.1f}%",
                "intervention_success": features.intervention_response.intervention_success_flag
            }
        }
    
    @staticmethod
    def _format_scores(
        features: ComprehensiveFeatureSet,
        classification: DropoutClassification
    ) -> Dict:
        """Format LMI and DRS scores."""
        return {
            "lmi": {
                "score": classification.lmi_score,
                "status": TeacherView._get_lmi_status(classification.lmi_score),
                "interpretation": TeacherView._interpret_lmi(classification.lmi_score)
            },
            "drs": {
                "score": classification.drs_score,
                "level": TeacherView._get_drs_level(classification.drs_score),
                "interpretation": TeacherView._interpret_drs(classification.drs_score)
            }
        }
    
    @staticmethod
    def _get_lmi_status(lmi: float) -> str:
        if lmi > 70:
            return "HEALTHY ✓"
        elif lmi > 40:
            return "AT_RISK ⚠"
        else:
            return "CRITICAL ✗"
    
    @staticmethod
    def _interpret_lmi(lmi: float) -> str:
        if lmi > 70:
            return "Learning momentum is strong. Student is progressing well."
        elif lmi > 40:
            return "Learning momentum is declining. Intervention may be helpful."
        else:
            return "Learning momentum is critically low. Urgent intervention needed."
    
    @staticmethod
    def _get_drs_level(drs: float) -> str:
        if drs < 0.3:
            return "LOW"
        elif drs < 0.6:
            return "MEDIUM"
        elif drs < 0.8:
            return "HIGH"
        else:
            return "CRITICAL"
    
    @staticmethod
    def _interpret_drs(drs: float) -> str:
        if drs < 0.3:
            return "Low dropout risk. Continue regular monitoring."
        elif drs < 0.6:
            return "Moderate dropout risk. Consider proactive support."
        elif drs < 0.8:
            return "High dropout risk. Intervention recommended."
        else:
            return "Critical dropout risk. Immediate intervention needed."
    
    @staticmethod
    def _format_intervention(classification: DropoutClassification) -> Dict:
        """Format intervention recommendation."""
        threshold_manager = ThresholdManager()
        urgency = threshold_manager.get_urgency_level(
            type('obj', (), {'drs_score': classification.drs_score, 'risk_level': 'HIGH' if classification.is_dropout else 'LOW'})()
        )
        
        return {
            "should_intervene": classification.is_dropout,
            "recommendation": classification.recommendation,
            "urgency": urgency,
            "follow_up_in_hours": TeacherView._suggest_follow_up_time(classification.drs_score)
        }
    
    @staticmethod
    def _suggest_follow_up_time(drs: float) -> int:
        """Suggest follow-up time in hours."""
        if drs > 0.8:
            return 1  # Urgent
        elif drs > 0.6:
            return 6  # Same day
        elif drs > 0.3:
            return 24  # Next day
        else:
            return 72  # 3 days
    
    @staticmethod
    def _prepare_visualization_data(
        features: ComprehensiveFeatureSet,
        classification: DropoutClassification
    ) -> Dict:
        """Prepare data for graphs and visualizations."""
        return {
            "lmi_gauge": {
                "value": classification.lmi_score,
                "thresholds": [40, 70],
                "zones": ["Critical", "At-Risk", "Healthy"]
            },
            "drs_gauge": {
                "value": classification.drs_score * 100,  # Convert to 0-100
                "thresholds": [30, 60, 80],
                "zones": ["Low", "Medium", "High", "Critical"]
            },
            "signal_heatmap": {
                "learning_progress": features.learning_progress.improvement_score,
                "stagnation": min(100, features.stagnation.stagnation_severity),
                "behavioral": min(100, features.behavioral_disengagement.consistency_score),
                "engagement": 100 - min(100, features.behavioral_disengagement.consistency_score) if not features.behavioral_disengagement.average_gap_increasing else 50
            }
        }


# ====================
# MAIN DROPOUT DETECTION SYSTEM
# ====================

class DropoutDetectionSystem:
    """
    Main orchestrator for the complete Dropout Detection System.
    Manages all layers and provides interface for both views.
    """
    
    def __init__(self, llm_client=None):
        """Initialize complete system."""
        self.event_collector = EventCollector()
        self.feature_extractor = FeatureExtractor(self.event_collector)
        self.llm_analyzer = LLMAnalyzer(llm_client)
        self.scoring_engine = ScoringEngine()
        self.classifier = DropoutClassifier(self.scoring_engine)
        self.pipeline = DropoutDetectionPipeline(
            self.event_collector,
            self.feature_extractor,
            self.llm_analyzer,
            self.scoring_engine
        )
        
        # Store history for trending
        self.student_history: Dict[str, Dict] = {}
    
    def record_event(
        self,
        event_type: EventType,
        student_id: str,
        question_id: str,
        data: Optional[Dict] = None
    ) -> LearningEvent:
        """Record a learning event."""
        return self.event_collector.record_event(
            event_type, student_id, question_id, data
        )
    
    def analyze(
        self,
        student_id: str,
        question_id: str,
        question_context: Optional[str] = None,
        role: UserRole = UserRole.TEACHER
    ) -> Dict:
        """
        Analyze student progress and generate appropriate view.
        
        Args:
            student_id: Student identifier
            question_id: Question identifier
            question_context: Optional question text for LLM analysis
            role: User role (STUDENT or TEACHER)
        
        Returns:
            Appropriate view based on role (Student or Teacher)
        """
        # Get historical LMI for trending
        historical_lmi = self._get_historical_lmi(student_id, question_id)
        
        # Run complete analysis pipeline
        features, classification = self.pipeline.analyze_student_question(
            student_id, question_id, historical_lmi, question_context
        )
        
        # Store in history
        self._update_student_history(student_id, question_id, classification)
        
        # Return appropriate view
        if role == UserRole.STUDENT:
            return StudentView.generate_student_feedback(features, classification)
        else:
            intervention_history = self._get_intervention_history(student_id, question_id)
            return TeacherView.generate_teacher_report(
                student_id, question_id, features, classification, intervention_history
            )
    
    def _get_historical_lmi(self, student_id: str, question_id: str) -> Optional[List[float]]:
        """Retrieve historical LMI scores for a student-question."""
        key = f"{student_id}:{question_id}"
        if key in self.student_history:
            return [s.get("lmi_score", 0) for s in self.student_history[key].get("analyses", [])]
        return None
    
    def _update_student_history(
        self,
        student_id: str,
        question_id: str,
        classification: DropoutClassification
    ):
        """Update student history with latest analysis."""
        key = f"{student_id}:{question_id}"
        if key not in self.student_history:
            self.student_history[key] = {"analyses": [], "interventions": []}
        
        self.student_history[key]["analyses"].append({
            "timestamp": datetime.now(),
            "lmi_score": classification.lmi_score,
            "drs_score": classification.drs_score,
            "is_dropout": classification.is_dropout,
            "dropout_types": [dt.value for dt in classification.dropout_types]
        })
    
    def _get_intervention_history(self, student_id: str, question_id: str) -> List[Dict]:
        """Get intervention history for a student-question."""
        key = f"{student_id}:{question_id}"
        if key in self.student_history:
            return self.student_history[key].get("interventions", [])
        return []
    
    def flag_for_intervention(
        self,
        student_id: str,
        question_id: str,
        intervention_type: str,
        notes: str
    ):
        """Record that intervention was triggered for a student."""
        key = f"{student_id}:{question_id}"
        intervention = {
            "timestamp": datetime.now(),
            "type": intervention_type,
            "notes": notes
        }
        
        if key not in self.student_history:
            self.student_history[key] = {"analyses": [], "interventions": []}
        
        self.student_history[key]["interventions"].append(intervention)


# ====================
# DEMONSTRATION & TESTING
# ====================

def main():
    """
    Demonstration of the Dropout Detection System.
    Simulates a complete learning scenario with multiple attempts.
    """
    print("=" * 80)
    print("DROPOUT DETECTION SYSTEM - DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Initialize system
    system = DropoutDetectionSystem()
    
    student_id = "STU001"
    question_id = "Q001"
    question_context = "Solve: 2x + 5 = 13"
    
    # Simulate learning events
    print("📝 Simulating Learning Events...")
    print()
    
    # Session 1: First attempt
    system.record_event(
        EventType.QUESTION_START,
        student_id, question_id,
        {"question_content": question_context}
    )
    
    system.record_event(
        EventType.QUESTION_SUBMIT,
        student_id, question_id,
        {"answer": "x = 4", "is_correct": True, "time_spent_seconds": 120}
    )
    
    # Session 2: Student returns, struggles
    system.record_event(
        EventType.QUESTION_START,
        student_id, question_id
    )
    
    system.record_event(
        EventType.ANSWER_REVISION,
        student_id, question_id,
        {"original_answer": "x = 8", "revised_answer": "x = 6", "revision_reason": "Rechecked calculation"}
    )
    
    system.record_event(
        EventType.QUESTION_SUBMIT,
        student_id, question_id,
        {"answer": "x = 6", "is_correct": False, "time_spent_seconds": 300}
    )
    
    # Session 3: Third attempt after long break
    system.record_event(
        EventType.FOCUS_BLUR,
        student_id, question_id,
        {"idle_duration_seconds": 900}
    )
    
    system.record_event(
        EventType.QUESTION_SUBMIT,
        student_id, question_id,
        {"answer": "x = 5", "is_correct": False, "time_spent_seconds": 180}
    )
    
    print("✓ Events recorded:")
    print(f"  - Question started")
    print(f"  - 3 answer submissions (1 correct, 2 incorrect)")
    print(f"  - Focus loss: 900 seconds (15 minutes)")
    print()
    
    # Analyze from Teacher view
    print("=" * 80)
    print("TEACHER VIEW - Full Dropout Analysis")
    print("=" * 80)
    print()
    
    teacher_report = system.analyze(
        student_id, question_id,
        question_context,
        role=UserRole.TEACHER
    )
    
    # Pretty print report
    dropout_status = teacher_report["dropout_status"]
    print(f"Status: {dropout_status['icon']} {dropout_status['status']}")
    print(f"Confidence: {dropout_status['confidence']}")
    print()
    
    if dropout_status['status'] == "DROPOUT_DETECTED":
        print(f"Detected Types: {dropout_status['types_string']}")
        print(f"Reason: {dropout_status['reason']}")
        print()
    
    scores = teacher_report["scores"]
    print(f"Learning Momentum Index (LMI): {scores['lmi']['score']:.1f}/100 - {scores['lmi']['status']}")
    print(f"Dropout Risk Score (DRS): {scores['drs']['score']:.2f}/1.0 - {scores['drs']['level']}")
    print()
    
    print(f"Recommendation: {teacher_report['intervention']['recommendation']}")
    print()
    
    # Analyze from Student view
    print("=" * 80)
    print("STUDENT VIEW - Supportive Feedback")
    print("=" * 80)
    print()
    
    student_report = system.analyze(
        student_id, question_id,
        question_context,
        role=UserRole.STUDENT
    )
    
    print("💪 Your Strengths:")
    for strength in student_report["strengths"]:
        print(f"  • {strength}")
    print()
    
    if student_report["growth_areas"]:
        print("📈 Growth Areas:")
        for area in student_report["growth_areas"]:
            print(f"  • {area['area']}: {area['message']}")
        print()
    
    print(f"Next Steps: {student_report['difficulty_suggestion']}")
    print()
    print(f"Encouragement: \"{student_report['encouragement']}\"")
    print()
    
    print("=" * 80)


if __name__ == "__main__":
    main()
