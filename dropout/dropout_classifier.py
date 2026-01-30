"""
Dropout Classification Layer
Implements rule + score hybrid logic for dropout classification.
"""

from typing import List, Optional, Tuple
from models import (
    ComprehensiveFeatureSet, DropoutClassification, DropoutType,
    LearningMomentumIndex, DropoutRiskScore
)
from scoring import ScoringEngine, ThresholdManager


class DropoutClassifier:
    """
    Classifies dropout into explicit types using rule + score hybrid approach.
    
    Rule hierarchy:
    1. Threshold-based rules (hard constraints)
    2. Score-based synthesis (soft constraints)
    3. Context-aware reasoning (final decision)
    """
    
    def __init__(self, scoring_engine: Optional[ScoringEngine] = None):
        self.scoring_engine = scoring_engine or ScoringEngine()
    
    def classify(
        self,
        features: ComprehensiveFeatureSet,
        historical_lmi: Optional[List[float]] = None
    ) -> DropoutClassification:
        """
        Classify student dropout status.
        
        Returns:
            DropoutClassification with types, reasons, and recommendations
        """
        # Calculate scores
        lmi = self.scoring_engine.calculate_lmi(features, historical_lmi)
        drs = self.scoring_engine.calculate_drs(features)
        
        # Apply classification rules
        dropout_types = self._determine_dropout_types(features, lmi, drs)
        is_dropout = len(dropout_types) > 0
        
        # Generate reasoning
        primary_reason = self._generate_primary_reason(dropout_types, features, lmi, drs)
        recommendation = self._generate_recommendation(dropout_types, drs)
        
        # Get risk factors
        risk_factors = drs.primary_risk_factors if drs else []
        
        # Determine confidence
        confidence = self._calculate_classification_confidence(
            is_dropout, dropout_types, drs, lmi
        )
        
        return DropoutClassification(
            is_dropout=is_dropout,
            dropout_types=dropout_types,
            primary_reason=primary_reason,
            lmi_score=lmi.lmi_score,
            drs_score=drs.drs_score,
            confidence=confidence,
            recommendation=recommendation,
            primary_risk_factors=risk_factors
        )
    
    # ====================
    # DROPOUT TYPE DETECTION
    # ====================
    
    def _determine_dropout_types(
        self,
        features: ComprehensiveFeatureSet,
        lmi: LearningMomentumIndex,
        drs: DropoutRiskScore
    ) -> List[DropoutType]:
        """
        Determine which types of dropout are present.
        Can be multiple types simultaneously.
        """
        types = []
        
        # Rule 1: COGNITIVE DROPOUT
        if self._is_cognitive_dropout(features, lmi):
            types.append(DropoutType.COGNITIVE)
        
        # Rule 2: BEHAVIORAL DROPOUT
        if self._is_behavioral_dropout(features):
            types.append(DropoutType.BEHAVIORAL)
        
        # Rule 3: ENGAGEMENT DROPOUT
        if self._is_engagement_dropout(features):
            types.append(DropoutType.ENGAGEMENT)
        
        # Rule 4: SILENT DROPOUT (Critical)
        if self._is_silent_dropout(features, lmi, drs):
            types.append(DropoutType.SILENT)
        
        return types
    
    def _is_cognitive_dropout(
        self,
        features: ComprehensiveFeatureSet,
        lmi: LearningMomentumIndex
    ) -> bool:
        """
        COGNITIVE DROPOUT: Understanding quality deteriorates.
        
        Indicators:
        - Shallow reasoning
        - Guessing patterns
        - Repeated misconceptions
        - No conceptual growth
        """
        progress = features.learning_progress
        ai_reasoning = features.ai_reasoning
        stagnation = features.stagnation
        
        # Rule: LMI < 40 AND low semantic change
        if lmi.lmi_score < ScoringEngine.LMI_AT_RISK:
            if progress.semantic_change_score < 30:
                return True
        
        # Rule: Multiple misconceptions detected
        if len(ai_reasoning.misconception_patterns) >= 2:
            if progress.improvement_score < 40:
                return True
        
        # Rule: No progress in semantic changes with multiple attempts
        if (progress.attempt_count >= 3 and
            progress.semantic_change_score < 20 and
            progress.improvement_score < 35):
            return True
        
        # Rule: Stalled with low reasoning consistency
        if stagnation.is_stalled and ai_reasoning.llm_confidence_estimate < 0.4:
            return True
        
        return False
    
    def _is_behavioral_dropout(self, features: ComprehensiveFeatureSet) -> bool:
        """
        BEHAVIORAL DROPOUT: Abnormal behavior patterns.
        
        Indicators:
        - Tab switching
        - Long inactivity gaps
        - Abrupt answer submissions
        - Erratic timing patterns
        """
        behavioral = features.behavioral_disengagement
        integrity = features.integrity
        
        # Rule: High consistency decline + average gap increasing
        if (behavioral.consistency_score < 40 and
            behavioral.average_gap_increasing):
            return True
        
        # Rule: Multiple focus losses (inactivity)
        events = getattr(features, '_events', [])  # Would need to pass events
        
        # Rule: Integrity concerns + behavioral changes
        if (integrity.external_assistance_likelihood > 0.7 and
            behavioral.consistency_score < 50):
            return True
        
        # Rule: Very long gaps between attempts (abandonment pattern)
        if behavioral.attempt_gap_time:
            if max(behavioral.attempt_gap_time) > 600:  # 10+ minutes
                return True
        
        return False
    
    def _is_engagement_dropout(self, features: ComprehensiveFeatureSet) -> bool:
        """
        ENGAGEMENT DROPOUT: Emotional or motivational decay.
        
        Indicators:
        - Reduced effort
        - Minimal explanations
        - Rapid disengagement after failure
        - Declining response richness
        """
        progress = features.learning_progress
        behavioral = features.behavioral_disengagement
        competition = features.competition_aware
        
        # Rule: Low attempt frequency with declining consistency
        if (progress.attempt_frequency < 0.2 and
            behavioral.consistency_score < 50):
            return True
        
        # Rule: Competition pressure + declining performance
        if (competition.competition_pressure_flag and
            progress.improvement_score < 40):
            return True
        
        # Rule: No progress flag + low consistency
        if (progress.no_progress_flag and
            behavioral.consistency_score < 60):
            return True
        
        # Rule: Average gap increasing significantly
        if (behavioral.average_gap_increasing and
            progress.attempt_count >= 3):
            return True
        
        return False
    
    def _is_silent_dropout(
        self,
        features: ComprehensiveFeatureSet,
        lmi: LearningMomentumIndex,
        drs: DropoutRiskScore
    ) -> bool:
        """
        SILENT DROPOUT: Most dangerous form.
        
        User appears active but learning momentum is collapsing silently.
        
        Indicators:
        - User appears active (events recorded)
        - Answers submitted
        - Scores exist
        - Learning momentum DECLINING SILENTLY
        """
        progress = features.learning_progress
        behavioral = features.behavioral_disengagement
        
        # Critical condition: LMI decelerating but behavior seems normal
        is_momentum_decelerating = (
            lmi.momentum_direction == "DECELERATING" and
            lmi.lmi_score < 50
        )
        
        # Behavior seems superficially normal
        behavior_appears_ok = (
            behavioral.consistency_score > 50 and
            not behavioral.average_gap_increasing
        )
        
        # But learning is actually stalling
        learning_stalling = (
            progress.semantic_change_score < 25 or
            progress.no_progress_flag
        )
        
        # Rule: Momentum decelerating + behavior ok + learning stalling
        if is_momentum_decelerating and behavior_appears_ok and learning_stalling:
            return True
        
        # Alternative: Low LMI with high DRS but no obvious red flags
        if (lmi.lmi_score < 35 and drs.drs_score > 0.7 and
            len(features.behavioral_disengagement.attempt_gap_time) == 0):
            return True
        
        return False
    
    # ====================
    # REASONING & RECOMMENDATIONS
    # ====================
    
    def _generate_primary_reason(
        self,
        dropout_types: List[DropoutType],
        features: ComprehensiveFeatureSet,
        lmi: LearningMomentumIndex,
        drs: DropoutRiskScore
    ) -> str:
        """Generate human-readable reason for dropout classification."""
        if not dropout_types:
            return "Student showing healthy learning progression"
        
        reasons = []
        
        for dtype in dropout_types:
            if dtype == DropoutType.COGNITIVE:
                gap = features.ai_reasoning.conceptual_gap_description or "Conceptual understanding declining"
                reasons.append(f"Cognitive: {gap}")
            
            elif dtype == DropoutType.BEHAVIORAL:
                reasons.append(
                    f"Behavioral: Inconsistent engagement pattern detected "
                    f"(consistency: {features.behavioral_disengagement.consistency_score:.0f}%)"
                )
            
            elif dtype == DropoutType.ENGAGEMENT:
                if features.competition_aware.competition_pressure_flag:
                    reasons.append("Engagement: Declining motivation due to competition pressure")
                else:
                    reasons.append("Engagement: Effort and focus declining over time")
            
            elif dtype == DropoutType.SILENT:
                reasons.append(
                    f"Silent: Learning momentum collapsing despite apparent activity "
                    f"(LMI: {lmi.lmi_score:.1f}, Trend: {lmi.momentum_direction.value})"
                )
        
        return " | ".join(reasons)
    
    def _generate_recommendation(
        self,
        dropout_types: List[DropoutType],
        drs: DropoutRiskScore
    ) -> str:
        """Generate intervention recommendation."""
        if not dropout_types:
            return "Continue monitoring. No immediate intervention needed."
        
        urgency = ThresholdManager.get_urgency_level(drs)
        intervention_type = ThresholdManager.get_intervention_type(drs)
        
        recommendations = {
            "CONCEPTUAL_SUPPORT": (
                "Provide step-by-step concept review and worked examples. "
                "Identify and address root misconceptions."
            ),
            "STRATEGIC_GUIDANCE": (
                "Teach problem-solving strategies. Break down complex problems. "
                "Provide hints before full solutions."
            ),
            "MOTIVATIONAL_SUPPORT": (
                "Acknowledge effort. Set achievable milestones. "
                "Connect learning to personal goals."
            ),
            "INTEGRITY_CHECK": (
                "Review learning authenticity. Provide supportive feedback. "
                "Adjust problem difficulty if needed."
            ),
            "GENERAL_SUPPORT": (
                "General learning support and encouragement."
            )
        }
        
        base_rec = recommendations.get(intervention_type, recommendations["GENERAL_SUPPORT"])
        
        urgency_prefix = {
            "URGENT": "⚠️ URGENT: ",
            "HIGH": "🔴 HIGH PRIORITY: ",
            "MEDIUM": "🟡 MEDIUM: ",
            "LOW": "🟢 LOW: "
        }
        
        return urgency_prefix.get(urgency, "") + base_rec
    
    def _calculate_classification_confidence(
        self,
        is_dropout: bool,
        dropout_types: List[DropoutType],
        drs: DropoutRiskScore,
        lmi: LearningMomentumIndex
    ) -> float:
        """
        Calculate confidence in the classification.
        Based on signal consistency and score magnitudes.
        """
        confidence = drs.confidence  # Base on DRS confidence
        
        # Boost confidence if multiple dropout types detected
        if len(dropout_types) > 1:
            confidence = min(1.0, confidence + 0.1)
        
        # Boost if LMI and DRS strongly agree
        if is_dropout:
            if lmi.lmi_score < 40 and drs.drs_score > 0.6:
                confidence = min(1.0, confidence + 0.15)
        else:
            if lmi.lmi_score > 70 and drs.drs_score < 0.3:
                confidence = min(1.0, confidence + 0.15)
        
        # Reduce confidence if signals conflict
        if is_dropout and drs.drs_score < 0.5:
            confidence = max(0.5, confidence - 0.1)
        
        return max(0.3, min(1.0, confidence))


class DropoutDetectionPipeline:
    """
    Complete pipeline from raw events to dropout classification.
    Orchestrates all five architectural layers.
    """
    
    def __init__(self, event_collector, feature_extractor, llm_analyzer, scoring_engine=None):
        self.event_collector = event_collector
        self.feature_extractor = feature_extractor
        self.llm_analyzer = llm_analyzer
        self.scoring_engine = scoring_engine or ScoringEngine()
        self.classifier = DropoutClassifier(self.scoring_engine)
    
    def analyze_student_question(
        self,
        student_id: str,
        question_id: str,
        historical_lmi: Optional[List[float]] = None,
        question_context: Optional[str] = None
    ) -> Tuple[ComprehensiveFeatureSet, DropoutClassification]:
        """
        Run complete analysis pipeline for a student-question pair.
        
        Returns:
            Tuple of (ComprehensiveFeatureSet, DropoutClassification)
        """
        # Layer 1: Events already collected (in event_collector)
        
        # Layer 2: Extract features
        features = self.feature_extractor.extract_comprehensive_features(student_id, question_id)
        
        # Layer 3: LLM analysis
        history = self.event_collector.build_attempt_history(student_id, question_id)
        ai_signals = self.llm_analyzer.analyze_attempt_progression(
            student_id, question_id, history, question_context
        )
        features.ai_reasoning = ai_signals
        
        # Layer 4 & 5: Scoring and classification
        classification = self.classifier.classify(features, historical_lmi)
        
        return features, classification
