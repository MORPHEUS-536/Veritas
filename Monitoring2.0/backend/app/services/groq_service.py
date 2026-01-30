"""
Groq LLM Service for Intelligent Monitoring
Provides LLM-based analysis using the Groq API.
Augments rule-based monitoring with intelligent insights.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.config import settings
from app.models.schemas import HealthStatus, MonitoringLog

logger = logging.getLogger(__name__)


class GroqLLMService:
    """
    Service for LLM-based intelligent monitoring using Groq API.
    Analyzes logs and data patterns to provide human-readable insights.
    """
    
    def __init__(self):
        """Initialize the Groq LLM service."""
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.max_tokens = settings.GROQ_MAX_TOKENS
        self.enabled = settings.ENABLE_LLM_MONITORING and bool(self.api_key)
        
        if self.enabled:
            logger.info(f"Groq LLM service initialized with model: {self.model}")
        else:
            logger.warning("Groq LLM service is disabled or API key is not configured")
    
    async def analyze_logs(
        self,
        logs: List[MonitoringLog],
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze monitoring logs using LLM to detect patterns and anomalies.
        
        Args:
            logs: List of monitoring logs to analyze
            focus_areas: Optional specific areas to focus the analysis on
            
        Returns:
            Dictionary with analysis, severity, findings, and recommendations
        """
        if not self.enabled:
            logger.warning("LLM analysis requested but service is disabled")
            return self._get_disabled_response()
        
        if not logs:
            logger.warning("LLM analysis requested with empty logs")
            return {
                "analysis": "No logs available for analysis.",
                "severity": HealthStatus.NORMAL,
                "key_findings": [],
                "recommendations": [],
                "confidence": 0.5
            }
        
        try:
            # Prepare the prompt with log data
            prompt = self._build_analysis_prompt(logs, focus_areas)
            
            # Call Groq API
            response = await self._call_groq_api(prompt)
            
            # Parse and structure the response
            structured_response = self._parse_llm_response(response, logs)
            
            logger.info(f"LLM analysis completed for {len(logs)} logs")
            return structured_response
            
        except Exception as e:
            logger.error(f"Error during LLM analysis: {str(e)}")
            return self._get_error_response(str(e))
    
    def _build_analysis_prompt(
        self,
        logs: List[MonitoringLog],
        focus_areas: Optional[List[str]] = None
    ) -> str:
        """Build a detailed prompt for LLM analysis."""
        # Summarize recent logs
        log_summary = self._summarize_logs(logs)
        
        focus_text = ""
        if focus_areas:
            focus_text = f"\nFocus on these areas: {', '.join(focus_areas)}"
        
        prompt = f"""You are a system monitoring expert analyzing application logs and metrics.

RECENT MONITORING DATA:
{log_summary}

YOUR TASK:
1. Analyze the patterns and anomalies in the monitoring data above
2. Identify root causes of any detected issues
3. Classify the overall system severity as NORMAL, WARNING, or CRITICAL
4. Provide specific, actionable recommendations
5. Rate your confidence in the analysis (0.0-1.0){focus_text}

RESPONSE FORMAT:
Provide a clear analysis with:
- ANALYSIS: A paragraph explaining what you found
- SEVERITY: One of NORMAL, WARNING, or CRITICAL
- KEY_FINDINGS: A numbered list of important observations
- RECOMMENDATIONS: A numbered list of recommended actions
- CONFIDENCE: A decimal number from 0.0 to 1.0

Be concise, technical, and focus on actionable insights."""

        return prompt
    
    def _summarize_logs(self, logs: List[MonitoringLog]) -> str:
        """Create a summary of logs for the LLM prompt."""
        # Count statuses
        status_counts = {"NORMAL": 0, "WARNING": 0, "CRITICAL": 0}
        issues = []
        sources = set()
        
        for log in logs:
            status = log.monitoring_result.status.value
            status_counts[status] += 1
            
            if log.monitoring_result.detected_issues:
                issues.extend(log.monitoring_result.detected_issues)
            
            sources.add(log.source)
        
        # Calculate average severity
        avg_severity = sum(log.monitoring_result.severity_score for log in logs) / len(logs) if logs else 0
        
        summary = f"""
Data Sources: {', '.join(sources)}
Total Events Analyzed: {len(logs)}
Status Distribution: NORMAL={status_counts['NORMAL']}, WARNING={status_counts['WARNING']}, CRITICAL={status_counts['CRITICAL']}
Average Severity Score: {avg_severity:.2f}

Detected Issues (aggregated):
"""
        if issues:
            unique_issues = list(set(issues))
            for issue in unique_issues[:10]:  # Limit to top 10
                summary += f"  - {issue}\n"
        else:
            summary += "  - None\n"
        
        # Add recent critical/warning logs
        critical_logs = [log for log in logs if log.monitoring_result.status != HealthStatus.NORMAL]
        if critical_logs:
            summary += f"\nRecent Issues ({len(critical_logs)} warnings/critical events):\n"
            for log in critical_logs[-5:]:  # Show last 5
                summary += f"  - [{log.monitoring_result.status.value}] {log.source}: {log.monitoring_result.reasoning}\n"
        
        return summary
    
    async def _call_groq_api(self, prompt: str) -> str:
        """
        Call the Groq API for text generation.
        
        In production, this would use the actual Groq SDK.
        For now, we simulate the response.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The LLM's response text
        """
        # Note: In production, use:
        # from groq import Groq
        # client = Groq(api_key=self.api_key)
        
        try:
            # Simulated API call - in production, use actual Groq client
            logger.info("Sending request to Groq API")
            
            # For demonstration, we'll create a structured response
            # In production, replace with actual API call:
            # response = client.chat.completions.create(
            #     model=self.model,
            #     messages=[{"role": "user", "content": prompt}],
            #     max_tokens=self.max_tokens,
            #     temperature=0.3
            # )
            # return response.choices[0].message.content
            
            # Simulated response for hackathon demo
            response = await self._simulate_groq_response(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Groq API call failed: {str(e)}")
            raise
    
    async def _simulate_groq_response(self, prompt: str) -> str:
        """
        Simulate a Groq API response for demonstration.
        Replace with actual API call in production.
        """
        # Simulate API latency
        await asyncio.sleep(0.5)
        
        # Return a sample structured response
        return """ANALYSIS:
System health shows mixed indicators. Most events are processing normally, but we've detected several concerning patterns. 
Response time degradation is visible in recent logs, suggesting potential resource constraints or network latency issues. 
The consistency of this pattern across multiple sources indicates a systemic issue rather than isolated failures.

SEVERITY: WARNING

KEY_FINDINGS:
1. Response times are trending upward over the monitored period
2. Multiple threshold violations detected in CPU and memory metrics
3. Error rate has increased by 15% compared to baseline patterns
4. Silent failures detected in data processing pipeline
5. No critical system failures, but performance degradation is evident

RECOMMENDATIONS:
1. Investigate resource utilization; consider horizontal scaling if under load
2. Review recent code deployments for performance regressions
3. Check network connectivity and service dependencies
4. Implement circuit breaker patterns to handle cascading failures
5. Set up automated alerts for the identified metrics to catch future issues earlier

CONFIDENCE: 0.82"""
    
    def _parse_llm_response(self, response: str, logs: List[MonitoringLog]) -> Dict[str, Any]:
        """
        Parse the LLM response into a structured format.
        
        Args:
            response: Raw LLM response text
            logs: Original logs used for analysis context
            
        Returns:
            Structured dictionary with parsed response
        """
        # Parse the response sections
        sections = {}
        current_section = None
        current_content = []
        
        for line in response.split("\n"):
            # Check for section headers
            if line.startswith("ANALYSIS:"):
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "ANALYSIS"
                current_content = [line.replace("ANALYSIS:", "").strip()]
            elif line.startswith("SEVERITY:"):
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "SEVERITY"
                current_content = [line.replace("SEVERITY:", "").strip()]
            elif line.startswith("KEY_FINDINGS:"):
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "KEY_FINDINGS"
                current_content = []
            elif line.startswith("RECOMMENDATIONS:"):
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "RECOMMENDATIONS"
                current_content = []
            elif line.startswith("CONFIDENCE:"):
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "CONFIDENCE"
                current_content = [line.replace("CONFIDENCE:", "").strip()]
            else:
                if current_section:
                    current_content.append(line)
        
        # Add the last section
        if current_section and current_content:
            sections[current_section] = "\n".join(current_content).strip()
        
        # Extract findings and recommendations
        key_findings = self._extract_list_items(sections.get("KEY_FINDINGS", ""))
        recommendations = self._extract_list_items(sections.get("RECOMMENDATIONS", ""))
        
        # Parse severity
        severity_str = sections.get("SEVERITY", "NORMAL").strip().upper()
        try:
            severity = HealthStatus[severity_str]
        except KeyError:
            severity = HealthStatus.NORMAL
        
        # Parse confidence
        try:
            confidence = float(sections.get("CONFIDENCE", "0.5"))
            confidence = max(0.0, min(1.0, confidence))  # Clamp to 0.0-1.0
        except (ValueError, TypeError):
            confidence = 0.5
        
        return {
            "analysis": sections.get("ANALYSIS", "Analysis could not be generated"),
            "severity": severity,
            "key_findings": key_findings,
            "recommendations": recommendations,
            "confidence": confidence
        }
    
    def _extract_list_items(self, text: str) -> List[str]:
        """Extract numbered list items from text."""
        items = []
        for line in text.split("\n"):
            line = line.strip()
            # Match lines like "1. Item" or "- Item"
            if line and (line[0].isdigit() or line.startswith("-")):
                # Remove numbering/bullet
                item = line.lstrip("0123456789.-) ").strip()
                if item:
                    items.append(item)
        return items
    
    def _get_disabled_response(self) -> Dict[str, Any]:
        """Return a response when LLM service is disabled."""
        return {
            "analysis": "LLM analysis is currently disabled. Enable ENABLE_LLM_MONITORING and provide GROQ_API_KEY to use this feature.",
            "severity": HealthStatus.NORMAL,
            "key_findings": ["LLM service is disabled"],
            "recommendations": ["Enable LLM monitoring by setting ENABLE_LLM_MONITORING=True and providing a valid GROQ_API_KEY"],
            "confidence": 0.0
        }
    
    def _get_error_response(self, error_message: str) -> Dict[str, Any]:
        """Return a response when an error occurs during LLM analysis."""
        return {
            "analysis": f"LLM analysis failed with error: {error_message}. Falling back to rule-based monitoring results.",
            "severity": HealthStatus.WARNING,
            "key_findings": [f"LLM analysis error: {error_message}"],
            "recommendations": ["Check API connectivity and configuration", "Review error logs for details"],
            "confidence": 0.3
        }
