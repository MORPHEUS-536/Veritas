"""
Core Monitoring Service
Implements the rule-based monitoring logic for detecting anomalies,
threshold violations, and suspicious patterns.
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from collections import deque
import statistics

from app.models.schemas import (
    MonitoringDataRequest,
    MonitoringLog,
    StatusEnum,
    LLMAnalysisResult
)
from app.config import (
    MAX_LOGS_STORED,
    ANOMALY_THRESHOLD_WARNING,
    ANOMALY_THRESHOLD_CRITICAL
)
from app.utils.logger import logger
from app.services.llm_service import llm_service


class MonitoringService:
    """
    Core monitoring service that processes incoming data,
    detects anomalies, and maintains logs.
    """
    
    def __init__(self):
        """Initialize the monitoring service."""
        # In-memory log storage (deque for efficient FIFO with max size)
        self.logs: deque = deque(maxlen=MAX_LOGS_STORED)
        
        # System health tracking
        self.start_time = datetime.utcnow()
        self.current_status = StatusEnum.NORMAL
        self.warning_count = 0
        self.critical_count = 0
        self.total_processed = 0
        self.last_critical_event: Optional[MonitoringLog] = None
        
        # Data history for pattern detection
        self.data_history: deque = deque(maxlen=100)
        
        logger.info("Monitoring service initialized")
    
    async def process_data(
        self,
        request: MonitoringDataRequest
    ) -> Tuple[MonitoringLog, str]:
        """
        Process incoming data and detect anomalies.
        
        Args:
            request: MonitoringDataRequest with data to monitor
            
        Returns:
            Tuple of (MonitoringLog, message)
        """
        self.total_processed += 1
        
        # Rule-based detection
        detected_status, reason = self._detect_anomalies(request)
        
        # Create log entry
        log_id = self._generate_log_id()
        log = MonitoringLog(
            log_id=log_id,
            timestamp=request.timestamp or datetime.utcnow(),
            source_module=request.source_module,
            event_type=request.event_type,
            input_data_snapshot=request.data,
            detected_status=detected_status,
            reason=reason
        )
        
        # Store in history for pattern detection
        self.data_history.append({
            "timestamp": log.timestamp,
            "source": request.source_module,
            "data": request.data,
            "status": detected_status
        })
        
        # Update system status
        self._update_system_status(detected_status, log)
        
        # Optional: LLM analysis (expensive, only if enabled)
        if llm_service.enabled and detected_status != StatusEnum.NORMAL:
            log = await self._enrich_with_llm_analysis(log)
        
        # Store log
        self.logs.append(log)
        
        logger.info(
            f"Processed data from {request.source_module}: "
            f"{detected_status.value} - {reason}"
        )
        
        return log, "Data monitored successfully"
    
    def _detect_anomalies(
        self,
        request: MonitoringDataRequest
    ) -> Tuple[StatusEnum, str]:
        """
        Apply rule-based anomaly detection logic.
        Checks for:
        - Threshold violations
        - Invalid data patterns
        - Suspicious values
        
        Args:
            request: Incoming data request
            
        Returns:
            Tuple of (StatusEnum, reason)
        """
        data = request.data
        source = request.source_module
        
        # Rule 1: Check for null/empty data
        if not data:
            return StatusEnum.CRITICAL, "Empty or null data received"
        
        # Rule 2: Check for timeout/latency issues
        if "latency_ms" in data:
            latency = data.get("latency_ms", 0)
            if latency > 5000:  # 5 seconds
                return StatusEnum.CRITICAL, f"Excessive latency detected: {latency}ms"
            elif latency > 2000:  # 2 seconds
                return StatusEnum.WARNING, f"High latency detected: {latency}ms"
        
        # Rule 3: Check prediction/score confidence
        if "prediction_score" in data or "confidence" in data:
            score = data.get("prediction_score") or data.get("confidence", 0)
            if score < 0 or score > 1:
                return StatusEnum.CRITICAL, f"Invalid score value: {score}"
            elif score < ANOMALY_THRESHOLD_CRITICAL:
                return StatusEnum.CRITICAL, f"Low prediction confidence: {score}"
            elif score < ANOMALY_THRESHOLD_WARNING:
                return StatusEnum.WARNING, f"Degraded prediction quality: {score}"
        
        # Rule 4: Detect sudden changes in data patterns
        status, reason = self._detect_pattern_anomalies(source, data)
        if status != StatusEnum.NORMAL:
            return status, reason
        
        # Rule 5: Check for error rates or failure indicators
        if "error_rate" in data:
            error_rate = data.get("error_rate", 0)
            if error_rate > 0.1:  # >10%
                return StatusEnum.CRITICAL, f"High error rate: {error_rate*100:.1f}%"
            elif error_rate > 0.05:  # >5%
                return StatusEnum.WARNING, f"Elevated error rate: {error_rate*100:.1f}%"
        
        # Rule 6: Check for data consistency
        status, reason = self._check_data_consistency(data)
        if status != StatusEnum.NORMAL:
            return status, reason
        
        # All checks passed
        return StatusEnum.NORMAL, "All metrics within acceptable range"
    
    def _detect_pattern_anomalies(
        self,
        source: str,
        data: dict
    ) -> Tuple[StatusEnum, str]:
        """
        Detect anomalies based on data patterns and trends.
        Uses statistical analysis on recent data.
        
        Args:
            source: Source module name
            data: Current data
            
        Returns:
            Tuple of (StatusEnum, reason)
        """
        # Get recent data from same source
        recent_data = [
            h["data"] for h in self.data_history
            if h["source"] == source and "value" in h["data"]
        ]
        
        if len(recent_data) < 5:
            return StatusEnum.NORMAL, ""  # Not enough data for pattern analysis
        
        try:
            # Calculate statistics
            recent_values = [h.get("value", 0) for h in recent_data[-10:]]
            mean = statistics.mean(recent_values)
            stdev = statistics.stdev(recent_values) if len(recent_values) > 1 else 0
            
            current_value = data.get("value", 0)
            
            # Check if current value is an outlier (> 3 standard deviations)
            if stdev > 0:
                z_score = abs((current_value - mean) / stdev)
                if z_score > 3:
                    return StatusEnum.WARNING, f"Potential outlier detected (z-score: {z_score:.2f})"
            
        except (ValueError, StatisticsError):
            pass  # Ignore statistical errors
        
        return StatusEnum.NORMAL, ""
    
    def _check_data_consistency(self, data: dict) -> Tuple[StatusEnum, str]:
        """
        Check for data type consistency and logical validity.
        
        Args:
            data: Data to check
            
        Returns:
            Tuple of (StatusEnum, reason)
        """
        # Check for required fields based on context
        if "status" in data:
            valid_statuses = ["success", "failed", "pending", "processing"]
            if data["status"] not in valid_statuses:
                return StatusEnum.WARNING, f"Unknown status value: {data['status']}"
        
        # Check for negative values where they shouldn't be
        if "count" in data and data["count"] < 0:
            return StatusEnum.CRITICAL, "Negative count value detected"
        
        if "duration_ms" in data and data["duration_ms"] < 0:
            return StatusEnum.CRITICAL, "Negative duration detected"
        
        return StatusEnum.NORMAL, ""
    
    def _update_system_status(
        self,
        detected_status: StatusEnum,
        log: MonitoringLog
    ) -> None:
        """
        Update overall system status based on latest detection.
        
        Args:
            detected_status: Status of the latest detection
            log: The monitoring log entry
        """
        if detected_status == StatusEnum.CRITICAL:
            self.critical_count += 1
            self.last_critical_event = log
            self.current_status = StatusEnum.CRITICAL
        elif detected_status == StatusEnum.WARNING:
            self.warning_count += 1
            # Only change to WARNING if not already CRITICAL
            if self.current_status != StatusEnum.CRITICAL:
                self.current_status = StatusEnum.WARNING
        
        # Downgrade status if things improve (simple heuristic)
        if detected_status == StatusEnum.NORMAL:
            if self.current_status == StatusEnum.WARNING and self.warning_count < 5:
                self.current_status = StatusEnum.NORMAL
    
    async def _enrich_with_llm_analysis(
        self,
        log: MonitoringLog
    ) -> MonitoringLog:
        """
        Optionally enrich log with LLM-based analysis.
        Only done for WARNING/CRITICAL events.
        
        Args:
            log: Monitoring log to enrich
            
        Returns:
            Enriched log with LLM analysis
        """
        try:
            # Get recent logs for context
            recent_logs = list(self.logs)[-20:]
            if not recent_logs:
                recent_logs = [log]
            
            # Call LLM service
            analysis = await llm_service.analyze_logs(recent_logs)
            
            if analysis:
                log.llm_analysis = analysis.analysis
                log.llm_suggestions = analysis.suggestions
                logger.info(f"LLM analysis completed for log {log.log_id}")
            
        except Exception as e:
            logger.error(f"Error during LLM enrichment: {str(e)}")
        
        return log
    
    def get_recent_logs(
        self,
        limit: int = 50
    ) -> List[MonitoringLog]:
        """
        Get recent monitoring logs.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of recent logs
        """
        logs = list(self.logs)
        return logs[-limit:] if logs else []
    
    def get_logs_by_status(
        self,
        status: StatusEnum,
        limit: int = 50
    ) -> List[MonitoringLog]:
        """
        Get logs filtered by status.
        
        Args:
            status: Status to filter by
            limit: Maximum number of logs
            
        Returns:
            List of matching logs
        """
        matching = [
            log for log in self.logs
            if log.detected_status == status
        ]
        return matching[-limit:] if matching else []
    
    def get_logs_by_source(
        self,
        source: str,
        limit: int = 50
    ) -> List[MonitoringLog]:
        """
        Get logs filtered by source module.
        
        Args:
            source: Source module name
            limit: Maximum number of logs
            
        Returns:
            List of matching logs
        """
        matching = [
            log for log in self.logs
            if log.source_module == source
        ]
        return matching[-limit:] if matching else []
    
    def get_system_health(self) -> dict:
        """
        Get current system health snapshot.
        
        Returns:
            Dict with health metrics
        """
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            "current_status": self.current_status,
            "total_logs_processed": self.total_processed,
            "warning_count": self.warning_count,
            "critical_count": self.critical_count,
            "last_update": datetime.utcnow(),
            "uptime_seconds": uptime,
            "last_critical_event": self.last_critical_event,
            "total_logs_stored": len(self.logs)
        }
    
    def clear_logs(self) -> int:
        """
        Clear all stored logs (useful for testing/reset).
        
        Returns:
            Number of logs cleared
        """
        count = len(self.logs)
        self.logs.clear()
        self.data_history.clear()
        logger.info(f"Cleared {count} logs")
        return count
    
    def _generate_log_id(self) -> str:
        """
        Generate unique log ID.
        
        Returns:
            Unique log ID string
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique = str(uuid.uuid4())[:8]
        return f"log_{timestamp}_{unique}"


# Create singleton instance
monitoring_service = MonitoringService()
