"""
LLM Analysis Layer
Performs cognitive reasoning analysis on attempt history.
Uses LLM for deep learning pattern recognition.
"""

import json
from typing import Dict, List, Optional
from models import (
    AIReasoningSignals, AttemptHistory, ComprehensiveFeatureSet
)
from event_collector import EventCollector


class LLMAnalyzer:
    """
    Analyzes reasoning quality and learning patterns using LLM.
    Produces structured cognitive insights.
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize LLM Analyzer.
        
        Args:
            llm_client: Optional LLM client (OpenAI, Anthropic, etc.)
                       If None, uses mock analysis for demonstration
        """
        self.llm_client = llm_client
        self.use_mock = llm_client is None
    
    def analyze_attempt_progression(
        self,
        student_id: str,
        question_id: str,
        history: AttemptHistory,
        question_context: Optional[str] = None
    ) -> AIReasoningSignals:
        """
        Analyze cognitive progression across attempts.
        
        Args:
            student_id: Student identifier
            question_id: Question identifier
            history: Complete attempt history
            question_context: Original question text/context
        
        Returns:
            Structured AI reasoning signals
        """
        if not history.attempts:
            return AIReasoningSignals(
                conceptual_gap_description="No attempts recorded",
                learning_summary="Student has not attempted this question",
                llm_confidence_estimate=0.0
            )
        
        if self.use_mock:
            return self._mock_analysis(history, question_context)
        
        return self._real_llm_analysis(history, question_context)
    
    def _mock_analysis(
        self,
        history: AttemptHistory,
        question_context: Optional[str]
    ) -> AIReasoningSignals:
        """
        Mock LLM analysis for demonstration.
        Replace with real LLM calls in production.
        """
        attempt_count = history.attempt_count
        correct_attempts = sum(1 for a in history.attempts if a.get("is_correct"))
        
        # Mock reasoning depth
        if attempt_count == 1:
            if correct_attempts == 1:
                reasoning_depth = 85
                conceptual_gap = "No gaps detected - solved on first attempt"
            else:
                reasoning_depth = 40
                conceptual_gap = "Initial misconception or insufficient understanding"
        elif attempt_count == 2:
            if correct_attempts >= 1:
                reasoning_depth = 70
                conceptual_gap = "Quick recovery suggests understanding refinement"
            else:
                reasoning_depth = 35
                conceptual_gap = "Persistent conceptual confusion"
        else:  # 3+ attempts
            if correct_attempts >= 1:
                reasoning_depth = 55
                conceptual_gap = "Difficulty with problem-solving approach, not concept"
            else:
                reasoning_depth = 20
                conceptual_gap = "Fundamental misunderstanding - requires intervention"
        
        # Mock conceptual consistency
        answer_lengths = [len(a.get("answer", "")) for a in history.attempts]
        if len(answer_lengths) > 1:
            variance = max(answer_lengths) - min(answer_lengths)
            if variance > 50:
                consistency = "LOW"
            elif variance > 20:
                consistency = "MEDIUM"
            else:
                consistency = "HIGH"
        else:
            consistency = "HIGH"
        
        # Mock misconception patterns
        misconceptions = []
        if attempt_count >= 2 and not correct_attempts:
            misconceptions.append("Repeated error pattern detected")
        
        # Mock confidence vs correctness gap
        if correct_attempts > 0:
            confidence_gap = -10  # Negative = correctly confident
        else:
            confidence_gap = 30  # Positive = overconfident or confused
        
        learning_summary = (
            f"Student made {attempt_count} attempt(s), "
            f"succeeded on {correct_attempts}. "
            f"Learning state: {consistency} consistency, "
            f"reasoning depth {reasoning_depth}/100. "
        )
        
        if misconceptions:
            learning_summary += f"Concerns: {', '.join(misconceptions)}"
        
        return AIReasoningSignals(
            conceptual_gap_description=conceptual_gap,
            learning_summary=learning_summary,
            llm_confidence_estimate=min(0.95, 0.5 + (attempt_count * 0.15)),
            misconception_patterns=misconceptions,
            confidence_vs_correctness_gap=confidence_gap
        )
    
    def _real_llm_analysis(
        self,
        history: AttemptHistory,
        question_context: Optional[str]
    ) -> AIReasoningSignals:
        """
        Real LLM analysis using configured client.
        """
        # Prepare prompt for LLM
        prompt = self._build_analysis_prompt(history, question_context)
        
        try:
            # Call LLM
            response = self.llm_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert learning analyst. Analyze student attempts and provide structured reasoning insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            # Parse structured response
            result = json.loads(response.choices[0].message.content)
            
            return AIReasoningSignals(
                conceptual_gap_description=result.get("conceptual_gap", ""),
                learning_summary=result.get("summary", ""),
                llm_confidence_estimate=result.get("confidence", 0.0),
                misconception_patterns=result.get("misconceptions", []),
                confidence_vs_correctness_gap=result.get("confidence_gap", 0.0)
            )
        
        except Exception as e:
            print(f"LLM analysis failed: {e}. Falling back to mock analysis.")
            return self._mock_analysis(history, question_context)
    
    def _build_analysis_prompt(
        self,
        history: AttemptHistory,
        question_context: Optional[str]
    ) -> str:
        """Build detailed prompt for LLM analysis."""
        attempts_text = "\n".join([
            f"Attempt {i+1} (timestamp: {a['timestamp']}):\n"
            f"  Answer: {a['answer']}\n"
            f"  Correct: {a['is_correct']}"
            for i, a in enumerate(history.attempts)
        ])
        
        context_text = f"Question context: {question_context}\n" if question_context else ""
        
        prompt = f"""Analyze the following student's attempts on a question and provide structured insights.

{context_text}
Attempt History:
{attempts_text}

Provide your analysis as JSON with the following structure:
{{
    "conceptual_gap": "Description of what conceptual gaps exist",
    "summary": "Brief learning progress summary",
    "confidence": 0.0-1.0,
    "misconceptions": ["pattern1", "pattern2"],
    "confidence_gap": -50 to +50 (negative = appropriately confident, positive = overconfident/confused)
}}

Analyze:
1. Whether the student shows conceptual understanding or just guessing
2. If there's a consistent pattern in errors or revisions
3. Learning progression from first to last attempt
4. Confidence indicators based on answer quality
5. Type of help needed (conceptual, strategic, or motivational)
"""
        return prompt
    
    def analyze_multiple_questions(
        self,
        student_id: str,
        question_histories: Dict[str, AttemptHistory],
        question_contexts: Optional[Dict[str, str]] = None
    ) -> Dict[str, AIReasoningSignals]:
        """
        Batch analyze multiple questions for a student.
        """
        results = {}
        for question_id, history in question_histories.items():
            context = question_contexts.get(question_id) if question_contexts else None
            results[question_id] = self.analyze_attempt_progression(
                student_id, question_id, history, context
            )
        return results
    
    def generate_learning_insights(
        self,
        features: ComprehensiveFeatureSet
    ) -> str:
        """
        Generate human-readable learning insights from features.
        """
        ai_signals = features.ai_reasoning
        progress_signals = features.learning_progress
        stagnation_signals = features.stagnation
        
        insights = []
        
        # Learning progress
        if progress_signals.learning_state.value == "PROGRESSING":
            insights.append("✓ Making consistent progress on this topic")
        elif progress_signals.learning_state.value == "PLATEAU":
            insights.append("⚠ Progress has plateaued - might need different approach")
        else:
            insights.append("✗ Learning stalled - intervention recommended")
        
        # Conceptual understanding
        if ai_signals.conceptual_gap_description:
            insights.append(f"Gap: {ai_signals.conceptual_gap_description}")
        
        # Misconceptions
        if ai_signals.misconception_patterns:
            insights.append(f"Patterns: {', '.join(ai_signals.misconception_patterns)}")
        
        # Stagnation warning
        if stagnation_signals.is_stalled:
            insights.append(
                f"⚠ Stuck for {stagnation_signals.stagnation_duration_minutes:.0f} minutes "
                f"across {stagnation_signals.repeat_attempt_count} attempts"
            )
        
        return "\n".join(insights) if insights else "No significant insights at this time."
    
    @staticmethod
    def format_structured_output(signals: AIReasoningSignals) -> Dict:
        """Convert AI signals to structured JSON output."""
        return {
            "conceptual_gap_description": signals.conceptual_gap_description,
            "learning_summary": signals.learning_summary,
            "llm_confidence_estimate": signals.llm_confidence_estimate,
            "misconception_patterns": signals.misconception_patterns,
            "confidence_vs_correctness_gap": signals.confidence_vs_correctness_gap
        }
