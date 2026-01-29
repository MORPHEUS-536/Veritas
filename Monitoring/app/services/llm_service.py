"""
LLM Integration Service
Handles interaction with LLM providers (OpenAI, Claude, Gemini).
Provides intelligent monitoring analysis and suggestions.
"""

import json
from typing import List, Optional
from datetime import datetime
from app.config import (
    ENABLE_LLM_MONITORING,
    LLM_PROVIDER,
    LLM_API_KEY,
    LLM_MODEL,
    LLM_MAX_TOKENS
)
from app.models.schemas import (
    LLMAnalysisResult,
    StatusEnum,
    MonitoringLog
)
from app.utils.logger import logger


class LLMService:
    """
    Service for LLM-based intelligent monitoring.
    Supports multiple LLM providers via abstraction layer.
    """
    
    def __init__(self):
        """Initialize LLM service with configured provider."""
        self.enabled = ENABLE_LLM_MONITORING
        self.provider = LLM_PROVIDER
        self.api_key = LLM_API_KEY
        self.model = LLM_MODEL
        self.max_tokens = LLM_MAX_TOKENS
        
        if self.enabled:
            self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the specific LLM provider client."""
        try:
            if self.provider == "openai":
                try:
                    import openai
                    openai.api_key = self.api_key
                    self.client = openai.OpenAI(api_key=self.api_key)
                    logger.info("OpenAI client initialized")
                except ImportError:
                    logger.warning("openai library not found. Install with: pip install openai")
                    self.enabled = False
                    
            elif self.provider == "claude":
                try:
                    import anthropic
                    self.client = anthropic.Anthropic(api_key=self.api_key)
                    logger.info("Anthropic (Claude) client initialized")
                except ImportError:
                    logger.warning("anthropic library not found. Install with: pip install anthropic")
                    self.enabled = False
                    
            elif self.provider == "gemini":
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=self.api_key)
                    self.client = genai.GenerativeModel(self.model)
                    logger.info("Google Gemini client initialized")
                except ImportError:
                    logger.warning("google-generativeai library not found. Install with: pip install google-generativeai")
                    self.enabled = False
            else:
                logger.error(f"Unknown LLM provider: {self.provider}")
                self.enabled = False
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM provider: {str(e)}")
            self.enabled = False
    
    async def analyze_logs(
        self,
        logs: List[MonitoringLog],
        focus_area: Optional[str] = None
    ) -> Optional[LLMAnalysisResult]:
        """
        Analyze recent monitoring logs using LLM.
        Classifies system state and provides recommendations.
        
        Args:
            logs: List of recent monitoring logs
            focus_area: Optional specific area to focus analysis on
            
        Returns:
            LLMAnalysisResult with classification and suggestions, or None if disabled
        """
        if not self.enabled:
            logger.debug("LLM monitoring is disabled")
            return None
        
        if not logs:
            logger.warning("No logs provided for LLM analysis")
            return None
        
        try:
            # Prepare log data for LLM analysis
            log_summary = self._prepare_log_summary(logs, focus_area)
            
            # Call appropriate LLM provider
            if self.provider == "openai":
                return await self._analyze_with_openai(log_summary)
            elif self.provider == "claude":
                return await self._analyze_with_claude(log_summary)
            elif self.provider == "gemini":
                return await self._analyze_with_gemini(log_summary)
            else:
                logger.error(f"Unknown provider: {self.provider}")
                return None
                
        except Exception as e:
            logger.error(f"Error during LLM analysis: {str(e)}")
            return None
    
    def _prepare_log_summary(
        self,
        logs: List[MonitoringLog],
        focus_area: Optional[str] = None
    ) -> str:
        """
        Prepare a structured summary of logs for LLM analysis.
        
        Args:
            logs: List of monitoring logs
            focus_area: Optional focus area
            
        Returns:
            Formatted string summary for LLM
        """
        summary_lines = [
            "=== MONITORING LOGS SUMMARY ===",
            f"Total logs analyzed: {len(logs)}",
            f"Time range: {logs[0].timestamp} to {logs[-1].timestamp}" if logs else "",
            ""
        ]
        
        # Count status distribution
        status_count = {}
        for log in logs:
            status_count[log.detected_status] = status_count.get(log.detected_status, 0) + 1
        
        summary_lines.append("STATUS DISTRIBUTION:")
        for status, count in status_count.items():
            summary_lines.append(f"  {status.value}: {count} occurrences")
        summary_lines.append("")
        
        # Recent events
        summary_lines.append("RECENT EVENTS (last 5):")
        for log in logs[-5:]:
            summary_lines.append(
                f"  [{log.timestamp}] {log.source_module}/{log.event_type}: "
                f"{log.detected_status.value} - {log.reason}"
            )
        summary_lines.append("")
        
        # Data patterns
        summary_lines.append("DATA PATTERNS:")
        for log in logs[-10:]:  # Last 10 logs
            summary_lines.append(f"  {log.source_module}: {json.dumps(log.input_data_snapshot, indent=2)}")
        
        if focus_area:
            summary_lines.append(f"\nFOCUS AREA: {focus_area}")
        
        return "\n".join(summary_lines)
    
    async def _analyze_with_openai(self, log_summary: str) -> Optional[LLMAnalysisResult]:
        """
        Analyze logs using OpenAI API.
        
        Args:
            log_summary: Formatted log summary
            
        Returns:
            LLMAnalysisResult or None
        """
        try:
            prompt = self._build_analysis_prompt(log_summary)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert system monitoring AI. Analyze the provided monitoring logs and classify the system state as 'normal', 'warning', or 'critical'. Provide clear explanations and actionable suggestions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            result_text = response.choices[0].message.content
            return self._parse_llm_response(result_text)
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return None
    
    async def _analyze_with_claude(self, log_summary: str) -> Optional[LLMAnalysisResult]:
        """
        Analyze logs using Claude API.
        
        Args:
            log_summary: Formatted log summary
            
        Returns:
            LLMAnalysisResult or None
        """
        try:
            prompt = self._build_analysis_prompt(log_summary)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system="You are an expert system monitoring AI. Analyze the provided monitoring logs and classify the system state as 'normal', 'warning', or 'critical'. Provide clear explanations and actionable suggestions.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            result_text = response.content[0].text
            return self._parse_llm_response(result_text)
            
        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            return None
    
    async def _analyze_with_gemini(self, log_summary: str) -> Optional[LLMAnalysisResult]:
        """
        Analyze logs using Google Gemini API.
        
        Args:
            log_summary: Formatted log summary
            
        Returns:
            LLMAnalysisResult or None
        """
        try:
            prompt = self._build_analysis_prompt(log_summary)
            
            response = self.client.generate_content(prompt)
            result_text = response.text
            return self._parse_llm_response(result_text)
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return None
    
    def _build_analysis_prompt(self, log_summary: str) -> str:
        """
        Build the prompt for LLM analysis.
        
        Args:
            log_summary: Log summary string
            
        Returns:
            Complete analysis prompt
        """
        return f"""
Analyze the following system monitoring logs:

{log_summary}

Please provide:
1. SYSTEM_STATE: Classify as one of [normal, warning, critical]
2. ANALYSIS: Explain what's happening in simple language (2-3 sentences)
3. SUGGESTIONS: List 3-5 specific, actionable recommendations
4. CONFIDENCE: Rate your confidence in this assessment (0.0-1.0)

Format your response as JSON with keys: system_state, analysis, suggestions (list), confidence
"""
    
    def _parse_llm_response(self, response_text: str) -> Optional[LLMAnalysisResult]:
        """
        Parse LLM response and extract structured data.
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            Structured LLMAnalysisResult or None
        """
        try:
            # Try to extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("Could not find JSON in LLM response")
                return self._create_default_analysis(response_text)
            
            json_str = response_text[json_start:json_end]
            parsed = json.loads(json_str)
            
            # Map response to LLMAnalysisResult
            system_state = parsed.get("system_state", "normal").lower()
            if system_state not in ["normal", "warning", "critical"]:
                system_state = "normal"
            
            return LLMAnalysisResult(
                system_state=StatusEnum(system_state),
                analysis=parsed.get("analysis", response_text),
                suggestions=parsed.get("suggestions", ["Continue monitoring"]),
                confidence=float(parsed.get("confidence", 0.8))
            )
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from LLM response, using fallback")
            return self._create_default_analysis(response_text)
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return None
    
    def _create_default_analysis(self, response_text: str) -> LLMAnalysisResult:
        """
        Create a default analysis result as fallback.
        
        Args:
            response_text: Raw response text to use as analysis
            
        Returns:
            Default LLMAnalysisResult
        """
        return LLMAnalysisResult(
            system_state=StatusEnum.NORMAL,
            analysis=response_text[:200] + "..." if len(response_text) > 200 else response_text,
            suggestions=["Review full logs", "Continue standard monitoring"],
            confidence=0.5
        )


# Create singleton instance
llm_service = LLMService()
