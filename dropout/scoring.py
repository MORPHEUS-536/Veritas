"""
Scoring & Thresholding Layer
Implements Learning Momentum Index (LMI) and Dropout Risk Score (DRS).
"""

from typing import List, Optional
from datetime import datetime
from models import (
    ComprehensiveFeatureSet, LearningMomentumIndex, DropoutRiskScore
)
import statistics


class ScoringEngine:
    """
    Calculates LMI (Learning Momentum Index) and DRS (Dropout Risk Score).
    Central decision-making engine for dropout detection.
    """
    
    # Thresholds
    LMI_HEALTHY = 70
    LMI_AT_RISK = 40
    DRS_LOW = 0.3
    DRS_MEDIUM = 0.6
    DRS_HIGH = 0.8
    
    def __init__(self):
        self.lmi_history: List[LearningMomentumIndex] = []
        self.drs_history: List[DropoutRiskScore] = []
    
    # ====================
    # LEARNING MOMENTUM INDEX (LMI)
    # ====================
    
    def calculate_lmi(
        self,
        features: ComprehensiveFeatureSet,
        historical_lmi: Optional[List[float]] = None
    ) -> LearningMomentumIndex:
        """
        Calculate Learning Momentum Index.
        
        LMI measures directional improvement of thinking quality across attempts.
        
        Scale: 0-100
        - LMI > 70 → Healthy learning
        - LMI 40-70 → At-risk
        - LMI < 40 → Dropout trajectory
        
        Non-linear decay: uses exponential weighting to emphasize recent attempts.
        """
        progress = features.learning_progress
        stagnation = features.stagnation
        integrity = features.integrity
        ai_reasoning = features.ai_reasoning
        
        # Base score from improvement signal
        base_improvement = progress.improvement_score  # 0-100
        
        # Adjustment 1: Semantic change quality
        semantic_bonus = (progress.semantic_change_score / 100) * 15  # +15 max
        
        # Adjustment 2: Stagnation penalty (non-linear decay)
        if stagnation.is_stalled:
            stagnation_penalty = 40  # Heavy penalty for stalled learning
        elif stagnation.stagnation_duration_minutes > 30:
            stagnation_penalty = 25
        elif stagnation.stagnation_duration_minutes > 15:
            stagnation_penalty = 15
        else:
            stagnation_penalty = 0
        
        # Adjustment 3: Learning state multiplier
        learning_state_multiplier = {
            "PROGRESSING": 1.2,
            "PLATEAU": 1.0,
            "STALLED": 0.5
        }.get(progress.learning_state.value, 1.0)
        
        # Adjustment 4: Integrity boost (trust in the learning signal)
        integrity_multiplier = integrity.integrity_score / 100  # 0-1
        
        # Adjustment 5: AI reasoning confidence
        llm_confidence = ai_reasoning.llm_confidence_estimate  # 0-1
        
        # Calculate momentum decay based on attempt history
        decay_rate = self._calculate_decay_rate(progress.attempt_count)
        
        # Combine all factors
        lmi_score = (
            (base_improvement * learning_state_multiplier + semantic_bonus)
            * integrity_multiplier
            * llm_confidence
            - stagnation_penalty
        )
        
        # Clamp to 0-100
        lmi_score = max(0, min(100, lmi_score))
        
        # Determine momentum direction based on historical trend
        if historical_lmi:
            if len(historical_lmi) >= 2:
                recent_trend = historical_lmi[-1] - historical_lmi[-2]
                if recent_trend > 5:
                    direction = "ACCELERATING"
                elif recent_trend < -5:
                    direction = "DECELERATING"
                else:
                    direction = "STABLE"
            else:
                direction = "STABLE"
        else:
            direction = "STABLE"
        
        lmi = LearningMomentumIndex(
            lmi_score=lmi_score,
            momentum_direction=direction,
            decay_rate=decay_rate,
            timestamp=datetime.now()
        )
        
        self.lmi_history.append(lmi)
        return lmi
    
    def _calculate_decay_rate(self, attempt_count: int) -> float:
        """
        Calculate exponential decay rate.
        More attempts without improvement = faster decay.
        """
        # Linear decay: each attempt after 2 reduces momentum
        base_decay = 0.05
        additional_decay = max(0, (attempt_count - 2) * 0.08)
        return base_decay + additional_decay
    
    # ====================
    # DROPOUT RISK SCORE (DRS)
    # ====================
    
    def calculate_drs(self, features: ComprehensiveFeatureSet) -> DropoutRiskScore:
        """
        Calculate Dropout Risk Score.
        
        Aggregates all signal categories into single actionable score.
        Scale: 0-1
        - 0-0.3: LOW risk
        - 0.3-0.6: MEDIUM risk
        - 0.6-0.8: HIGH risk
        - 0.8-1.0: CRITICAL risk
        """
        # Component scores (0-1)
        score_lmi = self._score_lmi_component(features)
        score_stagnation = self._score_stagnation_component(features)
        score_behavioral = self._score_behavioral_component(features)
        score_integrity = self._score_integrity_component(features)
        score_competition = self._score_competition_component(features)
        score_engagement = self._score_engagement_component(features)
        
        # Weighted aggregation
        weights = {
            "lmi": 0.35,              # Most important
            "stagnation": 0.25,       # Very important
            "behavioral": 0.15,
            "integrity": 0.10,
            "competition": 0.10,
            "engagement": 0.05
        }
        
        drs_score = (
            score_lmi * weights["lmi"] +
            score_stagnation * weights["stagnation"] +
            score_behavioral * weights["behavioral"] +
            score_integrity * weights["integrity"] +
            score_competition * weights["competition"] +
            score_engagement * weights["engagement"]
        )
        
        # Confidence based on signal quality
        confidence = self._calculate_drs_confidence(features)
        
        # Determine risk level
        if drs_score >= self.DRS_HIGH:
            risk_level = "CRITICAL"
        elif drs_score >= self.DRS_MEDIUM:
            risk_level = "HIGH"
        elif drs_score >= self.DRS_LOW:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Identify primary risk factors
        primary_factors = self._identify_risk_factors(
            score_lmi, score_stagnation, score_behavioral,
            score_integrity, score_competition, score_engagement
        )
        
        drs = DropoutRiskScore(
            drs_score=drs_score,
            confidence=confidence,
            risk_level=risk_level,
            primary_risk_factors=primary_factors,
            timestamp=datetime.now()
        )
        
        self.drs_history.append(drs)
        return drs
    
    def _score_lmi_component(self, features: ComprehensiveFeatureSet) -> float:
        """Convert LMI to 0-1 scale for DRS."""
        # Use historical LMI if available
        if self.lmi_history:
            lmi_score = self.lmi_history[-1].lmi_score
        else:
            lmi_score = features.learning_progress.improvement_score
        
        # Convert 0-100 scale to 0-1 inverse (high LMI = low risk)
        risk_score = 1.0 - (lmi_score / 100)
        return max(0, min(1, risk_score))
    
    def _score_stagnation_component(self, features: ComprehensiveFeatureSet) -> float:
        """Score stagnation risk (0-1)."""
        stagnation = features.stagnation
        
        if stagnation.is_stalled:
            return 0.95  # Near-critical stagnation
        
        # Linear scoring based on duration and repeat count
        duration_score = min(1.0, stagnation.stagnation_duration_minutes / 60)
        repeat_score = min(1.0, stagnation.repeat_attempt_count / 5)
        
        return (duration_score + repeat_score) / 2
    
    def _score_behavioral_component(self, features: ComprehensiveFeatureSet) -> float:
        """Score behavioral disengagement risk (0-1)."""
        disengagement = features.behavioral_disengagement
        
        risk = 0.0
        
        # Consistency penalty
        risk += (1.0 - disengagement.consistency_score / 100) * 0.4
        
        # Increasing gap penalty
        if disengagement.average_gap_increasing:
            risk += 0.3
        
        # Daily attempt reduction penalty (simplified for single session)
        if len(disengagement.daily_attempt_count) > 0 and disengagement.daily_attempt_count[0] < 3:
            risk += 0.3
        
        return min(1.0, risk)
    
    def _score_integrity_component(self, features: ComprehensiveFeatureSet) -> float:
        """Score integrity concerns (0-1)."""
        integrity = features.integrity
        
        risk = 0.0
        
        # Sudden jump flag
        if integrity.sudden_jump_flag:
            risk += 0.4
        
        # External assistance likelihood
        risk += integrity.external_assistance_likelihood * 0.3
        
        # Low continuity
        continuity_scores = {
            "HIGH": 0.0,
            "MEDIUM": 0.2,
            "LOW": 0.4
        }
        risk += continuity_scores.get(integrity.reasoning_continuity, 0.2)
        
        return min(1.0, risk)
    
    def _score_competition_component(self, features: ComprehensiveFeatureSet) -> float:
        """Score competition pressure risk (0-1)."""
        competition = features.competition_aware
        
        risk = 0.0
        
        if competition.competition_pressure_flag:
            risk += 0.5
        
        # Rank delta (worsening ranks increase risk)
        if competition.rank_delta and competition.rank_delta > 0:
            risk += min(0.4, competition.rank_delta / 100)
        
        # Low relative progress
        risk += (1.0 - competition.relative_progress_index / 100) * 0.3
        
        return min(1.0, risk)
    
    def _score_engagement_component(self, features: ComprehensiveFeatureSet) -> float:
        """Score engagement/disengagement risk (0-1)."""
        # Combines multiple engagement signals
        progress = features.learning_progress
        
        risk = 0.0
        
        # No progress flag
        if progress.no_progress_flag:
            risk += 0.6
        
        # Low attempt frequency
        if progress.attempt_frequency < 0.1:  # Less than 1 attempt per 10 minutes
            risk += 0.3
        
        return min(1.0, risk)
    
    def _calculate_drs_confidence(self, features: ComprehensiveFeatureSet) -> float:
        """
        Calculate confidence in the DRS score.
        Based on signal quality and evidence strength.
        """
        confidence = 0.5  # Base confidence
        
        # Increase confidence with more attempts
        attempt_boost = min(0.3, features.learning_progress.attempt_count * 0.05)
        confidence += attempt_boost
        
        # Increase with LLM confidence
        confidence += features.ai_reasoning.llm_confidence_estimate * 0.1
        
        # Decrease if signals conflict
        progress_ok = features.learning_progress.improvement_score > 50
        stagnation_bad = features.stagnation.is_stalled
        
        if progress_ok and stagnation_bad:
            confidence -= 0.15  # Conflicting signals
        
        return max(0.3, min(1.0, confidence))
    
    def _identify_risk_factors(
        self,
        score_lmi: float,
        score_stagnation: float,
        score_behavioral: float,
        score_integrity: float,
        score_competition: float,
        score_engagement: float
    ) -> List[str]:
        """Identify and rank primary risk factors."""
        factors = [
            ("Declining learning momentum", score_lmi) if score_lmi > 0.6 else None,
            ("Stagnation on problem", score_stagnation) if score_stagnation > 0.6 else None,
            ("Reduced effort/consistency", score_behavioral) if score_behavioral > 0.6 else None,
            ("Authenticity concerns", score_integrity) if score_integrity > 0.6 else None,
            ("Competition pressure", score_competition) if score_competition > 0.6 else None,
            ("Engagement declining", score_engagement) if score_engagement > 0.6 else None,
        ]
        
        # Filter None values and sort by score
        factors = [f for f in factors if f is not None]
        factors.sort(key=lambda x: x[1], reverse=True)
        
        return [f[0] for f in factors[:3]]  # Top 3 factors


class ThresholdManager:
    """
    Manages dropout detection thresholds and decision rules.
    """
    
    @staticmethod
    def should_flag_for_intervention(drs: DropoutRiskScore, lmi: LearningMomentumIndex) -> bool:
        """
        Determine if student should be flagged for intervention.
        
        Rules:
        1. DRS >= 0.6 (MEDIUM or higher) → Flag
        2. LMI < 40 → Flag
        3. Both metrics trending down → Flag
        """
        return (
            drs.drs_score >= ScoringEngine.DRS_MEDIUM
            or lmi.lmi_score < ScoringEngine.LMI_AT_RISK
        )
    
    @staticmethod
    def get_intervention_type(drs: DropoutRiskScore) -> str:
        """
        Recommend intervention type based on primary risk factors.
        """
        factors = drs.primary_risk_factors
        
        if "Declining learning momentum" in factors:
            return "CONCEPTUAL_SUPPORT"
        elif "Stagnation on problem" in factors:
            return "STRATEGIC_GUIDANCE"
        elif "Competition pressure" in factors or "Engagement declining" in factors:
            return "MOTIVATIONAL_SUPPORT"
        elif "Authenticity concerns" in factors:
            return "INTEGRITY_CHECK"
        else:
            return "GENERAL_SUPPORT"
    
    @staticmethod
    def get_urgency_level(drs: DropoutRiskScore) -> str:
        """Get urgency level for intervention."""
        if drs.risk_level == "CRITICAL":
            return "URGENT"
        elif drs.risk_level == "HIGH":
            return "HIGH"
        elif drs.risk_level == "MEDIUM":
            return "MEDIUM"
        else:
            return "LOW"
