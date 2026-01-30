"""
Rule-Based Monitoring Engine
Detects failures and anomalies through threshold violations,
invalid outputs, and abnormal behavioral patterns.
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
from collections import deque
from datetime import datetime, timedelta
from app.models.schemas import HealthStatus, MonitoringResult

logger = logging.getLogger(__name__)


class MonitoringEngine:
    """
    Core rule-based monitoring engine for detecting anomalies and failures.
    Supports threshold violations, consistency checks, and trend analysis.
    """
    
    def __init__(self, warning_threshold: float = 0.7, critical_threshold: float = 0.9):
        """
        Initialize the monitoring engine.
        
        Args:
            warning_threshold: Score above which status is WARNING (0.0-1.0)
            critical_threshold: Score above which status is CRITICAL (0.0-1.0)
        """
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        
        # Historical data for trend analysis (keep last 100 events per source)
        self.history: Dict[str, deque] = {}
        self.max_history_size = 100
        
        logger.info(f"Monitoring engine initialized with thresholds: warning={warning_threshold}, critical={critical_threshold}")
    
    def add_to_history(self, source: str, event_data: Dict[str, Any]):
        """Store event in historical data for trend analysis."""
        if source not in self.history:
            self.history[source] = deque(maxlen=self.max_history_size)
        self.history[source].append({
            "timestamp": datetime.utcnow(),
            "data": event_data
        })
    
    def analyze(self, source: str, event_type: str, data: Dict[str, Any]) -> MonitoringResult:
        """
        Analyze incoming event and detect anomalies.
        
        Args:
            source: Data source or module name
            event_type: Type of event
            data: Event data payload
            
        Returns:
            MonitoringResult with status, score, and reasoning
        """
        failed_rules = []
        detected_issues = []
        severity_score = 0.0
        
        # Rule 1: Check for null/invalid outputs
        if self._check_invalid_output(data):
            failed_rules.append("INVALID_OUTPUT")
            detected_issues.append("Invalid or null outputs detected")
            severity_score += 0.3
        
        # Rule 2: Check threshold violations
        threshold_violations = self._check_threshold_violations(source, event_type, data)
        if threshold_violations:
            failed_rules.extend(threshold_violations)
            for violation in threshold_violations:
                detected_issues.append(f"Threshold violation: {violation}")
            severity_score += 0.25 * len(threshold_violations)
        
        # Rule 3: Check for consistency issues
        if self._check_consistency(source, data):
            failed_rules.append("CONSISTENCY_CHECK")
            detected_issues.append("Consistency check failed")
            severity_score += 0.2
        
        # Rule 4: Check for abnormal patterns (trend analysis)
        anomaly_score = self._detect_anomalies(source, data)
        if anomaly_score > 0:
            failed_rules.append("ANOMALY_DETECTION")
            detected_issues.append("Abnormal pattern detected in historical data")
            severity_score += anomaly_score
        
        # Rule 5: Silent failure detection
        if self._detect_silent_failure(source, event_type, data):
            failed_rules.append("SILENT_FAILURE")
            detected_issues.append("Potential silent failure detected")
            severity_score += 0.4
        
        # Cap severity score at 1.0
        severity_score = min(severity_score, 1.0)
        
        # Add event to history for future trend analysis
        self.add_to_history(source, data)
        
        # Determine health status based on severity score
        if severity_score >= self.critical_threshold:
            status = HealthStatus.CRITICAL
        elif severity_score >= self.warning_threshold:
            status = HealthStatus.WARNING
        else:
            status = HealthStatus.NORMAL
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            status, severity_score, failed_rules, detected_issues, data
        )
        
        # Generate suggestions
        suggestions = self._generate_suggestions(status, failed_rules, detected_issues)
        
        return MonitoringResult(
            status=status,
            severity_score=round(severity_score, 3),
            reasoning=reasoning,
            detected_issues=detected_issues,
            suggestions=suggestions,
            failed_rules=failed_rules
        )
    
    def _check_invalid_output(self, data: Dict[str, Any]) -> bool:
        """Check for null, empty, or invalid outputs."""
        for key, value in data.items():
            if value is None:
                logger.debug(f"Invalid output detected: {key} is None")
                return True
            if isinstance(value, str) and value.lower() in ["error", "failed", "null"]:
                logger.debug(f"Invalid output detected: {key} = {value}")
                return True
            if isinstance(value, dict) and not value:  # Empty dict
                logger.debug(f"Invalid output detected: {key} is empty dict")
                return True
        return False
    
    def _check_threshold_violations(self, source: str, event_type: str, data: Dict[str, Any]) -> List[str]:
        """Check for threshold violations based on common metrics."""
        violations = []
        
        # Common metric checks
        metric_thresholds = {
            "response_time": 5000,  # milliseconds
            "cpu_usage": 90,  # percentage
            "memory_usage": 85,  # percentage
            "error_rate": 10,  # percentage
            "latency": 3000,  # milliseconds
        }
        
        for metric, threshold in metric_thresholds.items():
            if metric in data:
                value = data[metric]
                if isinstance(value, (int, float)) and value > threshold:
                    violations.append(f"{metric.upper()}_EXCEEDED")
                    logger.debug(f"Threshold violation: {metric}={value} > {threshold}")
        
        return violations
    
    def _check_consistency(self, source: str, data: Dict[str, Any]) -> bool:
        """Check for consistency issues across fields."""
        # Check if related fields have logical consistency
        if "status_code" in data and "response" in data:
            status_code = data.get("status_code")
            response = data.get("response")
            
            # Inconsistency: 200 status but error response
            if status_code == 200 and isinstance(response, str) and "error" in response.lower():
                logger.debug("Consistency check failed: 200 status with error response")
                return True
            
            # Inconsistency: 500 status but success response
            if status_code >= 500 and isinstance(response, str) and "success" in response.lower():
                logger.debug("Consistency check failed: 500 status with success response")
                return True
        
        return False
    
    def _detect_anomalies(self, source: str, data: Dict[str, Any]) -> float:
        """
        Detect anomalies using historical trend comparison.
        Returns anomaly score (0.0-0.3).
        """
        if source not in self.history or len(self.history[source]) < 5:
            # Not enough history for trend analysis
            return 0.0
        
        anomaly_score = 0.0
        
        # Check for outliers in numeric metrics
        for key, value in data.items():
            if not isinstance(value, (int, float)):
                continue
            
            # Get historical values for this metric
            historical_values = [
                event["data"].get(key)
                for event in self.history[source]
                if isinstance(event["data"].get(key), (int, float))
            ]
            
            if len(historical_values) < 5:
                continue
            
            # Calculate mean and standard deviation
            mean = sum(historical_values) / len(historical_values)
            variance = sum((x - mean) ** 2 for x in historical_values) / len(historical_values)
            std_dev = variance ** 0.5
            
            # If std_dev is 0, skip
            if std_dev == 0:
                continue
            
            # Calculate z-score
            z_score = abs((value - mean) / std_dev)
            
            # If z-score > 3, it's likely an anomaly
            if z_score > 3:
                logger.debug(f"Anomaly detected: {key} z-score = {z_score}")
                anomaly_score += 0.1
        
        return min(anomaly_score, 0.3)
    
    def _detect_silent_failure(self, source: str, event_type: str, data: Dict[str, Any]) -> bool:
        """
        Detect silent failures where system appears to work but produces wrong results.
        Check for patterns like: successful status but no actual data returned.
        """
        # Pattern 1: Success status but empty result
        if data.get("status") == "success" and data.get("result") is None:
            logger.debug("Silent failure detected: success status with None result")
            return True
        
        # Pattern 2: Processing reported but no output generated
        if data.get("processed", False) and not data.get("output"):
            logger.debug("Silent failure detected: processed=True but no output")
            return True
        
        # Pattern 3: Completion reported but zero items processed
        if data.get("completed", False) and data.get("items_processed", 0) == 0:
            logger.debug("Silent failure detected: completed=True but items_processed=0")
            return True
        
        return False
    
    def _generate_reasoning(
        self,
        status: HealthStatus,
        severity_score: float,
        failed_rules: List[str],
        detected_issues: List[str],
        data: Dict[str, Any]
    ) -> str:
        """Generate human-readable reasoning for the monitoring result."""
        if status == HealthStatus.NORMAL:
            return f"System is operating normally (severity: {severity_score}). All monitored metrics are within acceptable ranges."
        
        elif status == HealthStatus.WARNING:
            issues_text = "; ".join(detected_issues) if detected_issues else "Minor anomalies detected"
            return f"System requires attention (severity: {severity_score}). {issues_text}. Review and monitor for escalation."
        
        else:  # CRITICAL
            issues_text = "; ".join(detected_issues) if detected_issues else "Critical issues detected"
            return f"System is in critical state (severity: {severity_score}). {issues_text}. Immediate action required."
    
    def _generate_suggestions(self, status: HealthStatus, failed_rules: List[str], detected_issues: List[str]) -> List[str]:
        """Generate actionable suggestions based on detected issues."""
        suggestions = []
        
        if "INVALID_OUTPUT" in failed_rules:
            suggestions.append("Check data source for null/invalid outputs; validate data pipeline")
        
        if any("THRESHOLD" in rule for rule in failed_rules):
            suggestions.append("Review threshold-exceeding metrics; consider resource scaling")
        
        if "CONSISTENCY_CHECK" in failed_rules:
            suggestions.append("Investigate data consistency issues; check for data corruption")
        
        if "ANOMALY_DETECTION" in failed_rules:
            suggestions.append("Analyze recent patterns; compare with baseline behavior")
        
        if "SILENT_FAILURE" in failed_rules:
            suggestions.append("Verify data integrity; check for incomplete processing")
        
        if status == HealthStatus.CRITICAL:
            suggestions.insert(0, "URGENT: Initiate incident response protocol")
        
        return suggestions if suggestions else ["Monitor system closely for changes"]
    
    def get_history_summary(self, source: str) -> Dict[str, Any]:
        """Get summary of historical data for a source."""
        if source not in self.history or not self.history[source]:
            return {"source": source, "event_count": 0, "summary": "No historical data"}
        
        history = self.history[source]
        event_count = len(history)
        oldest_time = history[0]["timestamp"]
        latest_time = history[-1]["timestamp"]
        
        return {
            "source": source,
            "event_count": event_count,
            "oldest_event": oldest_time.isoformat(),
            "latest_event": latest_time.isoformat(),
            "time_span_seconds": (latest_time - oldest_time).total_seconds()
        }
