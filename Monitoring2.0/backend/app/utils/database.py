"""
Monitoring Logger and Database
Handles storage and retrieval of monitoring logs.
Uses in-memory storage with optional persistence.
"""

import logging
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import deque
from threading import Lock
import uuid

from app.models.schemas import MonitoringLog, HealthStatus
from app.config import settings

logger = logging.getLogger(__name__)


class MonitoringDatabase:
    """
    In-memory database for monitoring logs with optional file persistence.
    Thread-safe storage for monitoring events.
    """
    
    def __init__(self, max_entries: int = 10000, persistence_enabled: bool = False):
        """
        Initialize the monitoring database.
        
        Args:
            max_entries: Maximum number of logs to keep in memory
            persistence_enabled: Whether to persist logs to file
        """
        self.max_entries = max_entries
        self.persistence_enabled = persistence_enabled
        
        # In-memory storage (deque automatically removes oldest when max reached)
        self.logs: deque = deque(maxlen=max_entries)
        self.lock = Lock()
        
        # Index for faster queries
        self.status_index: Dict[HealthStatus, int] = {
            HealthStatus.NORMAL: 0,
            HealthStatus.WARNING: 0,
            HealthStatus.CRITICAL: 0,
        }
        
        logger.info(f"Monitoring database initialized with max_entries={max_entries}")
    
    def add_log(self, log: MonitoringLog) -> str:
        """
        Add a monitoring log to the database.
        
        Args:
            log: MonitoringLog to add
            
        Returns:
            Event ID
        """
        with self.lock:
            self.logs.append(log)
            
            # Update index
            status = log.monitoring_result.status
            self.status_index[status] = self.status_index.get(status, 0) + 1
            
            logger.debug(f"Log added: {log.event_id} - {status.value}")
        
        # Optional: persist to file
        if self.persistence_enabled:
            self._persist_log(log)
        
        return log.event_id
    
    def get_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        source: Optional[str] = None,
        status: Optional[HealthStatus] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> tuple[List[MonitoringLog], int]:
        """
        Query monitoring logs with filters.
        
        Args:
            limit: Maximum number of logs to return
            offset: Number of logs to skip
            source: Filter by data source
            status: Filter by health status
            start_time: Filter logs after this time
            end_time: Filter logs before this time
            
        Returns:
            Tuple of (filtered logs, total count)
        """
        with self.lock:
            # Apply filters
            filtered_logs = []
            
            for log in self.logs:
                # Source filter
                if source and log.source != source:
                    continue
                
                # Status filter
                if status and log.monitoring_result.status != status:
                    continue
                
                # Time range filters
                if start_time and log.timestamp < start_time:
                    continue
                if end_time and log.timestamp > end_time:
                    continue
                
                filtered_logs.append(log)
            
            total_count = len(filtered_logs)
            
            # Apply pagination
            result_logs = filtered_logs[offset : offset + limit]
            
            logger.debug(f"Query: returned {len(result_logs)}/{total_count} logs")
            
            return result_logs, total_count
    
    def get_recent_logs(self, lookback_minutes: int = 10) -> List[MonitoringLog]:
        """Get logs from the last N minutes."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=lookback_minutes)
        logs, _ = self.get_logs(
            limit=self.max_entries,
            start_time=cutoff_time
        )
        return logs
    
    def get_log_by_id(self, event_id: str) -> Optional[MonitoringLog]:
        """Get a specific log by event ID."""
        with self.lock:
            for log in self.logs:
                if log.event_id == event_id:
                    return log
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored logs."""
        with self.lock:
            total_logs = len(self.logs)
            
            if total_logs == 0:
                return {
                    "total_logs": 0,
                    "status_distribution": {
                        "NORMAL": 0,
                        "WARNING": 0,
                        "CRITICAL": 0,
                    },
                    "unique_sources": 0,
                    "unique_event_types": 0,
                    "avg_severity": 0.0,
                }
            
            # Calculate statistics
            sources = set()
            event_types = set()
            severity_sum = 0.0
            status_counts = {
                HealthStatus.NORMAL: 0,
                HealthStatus.WARNING: 0,
                HealthStatus.CRITICAL: 0,
            }
            
            for log in self.logs:
                sources.add(log.source)
                event_types.add(log.event_type)
                severity_sum += log.monitoring_result.severity_score
                status_counts[log.monitoring_result.status] += 1
            
            avg_severity = severity_sum / total_logs if total_logs > 0 else 0.0
            
            return {
                "total_logs": total_logs,
                "status_distribution": {
                    "NORMAL": status_counts[HealthStatus.NORMAL],
                    "WARNING": status_counts[HealthStatus.WARNING],
                    "CRITICAL": status_counts[HealthStatus.CRITICAL],
                },
                "unique_sources": len(sources),
                "unique_event_types": len(event_types),
                "avg_severity": round(avg_severity, 3),
                "oldest_log": self.logs[0].timestamp.isoformat() if self.logs else None,
                "newest_log": self.logs[-1].timestamp.isoformat() if self.logs else None,
            }
    
    def get_current_health_status(self) -> tuple[HealthStatus, float]:
        """
        Get the current overall system health status.
        Based on the most recent logs.
        
        Returns:
            Tuple of (status, average_severity)
        """
        with self.lock:
            if not self.logs:
                return HealthStatus.NORMAL, 0.0
            
            # Use last 100 logs or all if fewer
            recent_logs = list(self.logs)[-100:]
            
            # Count statuses
            status_counts = {
                HealthStatus.NORMAL: 0,
                HealthStatus.WARNING: 0,
                HealthStatus.CRITICAL: 0,
            }
            
            severity_sum = 0.0
            
            for log in recent_logs:
                status = log.monitoring_result.status
                status_counts[status] += 1
                severity_sum += log.monitoring_result.severity_score
            
            avg_severity = severity_sum / len(recent_logs) if recent_logs else 0.0
            
            # Determine overall status
            # If any critical, system is critical
            if status_counts[HealthStatus.CRITICAL] > 0:
                return HealthStatus.CRITICAL, round(avg_severity, 3)
            # If any warning, system is warning
            elif status_counts[HealthStatus.WARNING] > 0:
                return HealthStatus.WARNING, round(avg_severity, 3)
            # Otherwise normal
            else:
                return HealthStatus.NORMAL, round(avg_severity, 3)
    
    def clear_old_logs(self, older_than_minutes: int = 1440):
        """Remove logs older than specified minutes."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=older_than_minutes)
        
        with self.lock:
            original_count = len(self.logs)
            
            # Create new deque without old logs
            new_logs = deque(maxlen=self.max_entries)
            for log in self.logs:
                if log.timestamp >= cutoff_time:
                    new_logs.append(log)
            
            self.logs = new_logs
            removed_count = original_count - len(self.logs)
            
            if removed_count > 0:
                logger.info(f"Removed {removed_count} logs older than {older_than_minutes} minutes")
        
        return removed_count
    
    def _persist_log(self, log: MonitoringLog):
        """Persist a log to file (for durability)."""
        try:
            log_file = settings.LOG_FILE
            
            with open(log_file, 'a') as f:
                f.write(log.model_dump_json() + "\n")
            
        except Exception as e:
            logger.error(f"Failed to persist log to file: {str(e)}")


# Global database instance
monitoring_db = MonitoringDatabase(
    max_entries=settings.MAX_LOG_ENTRIES,
    persistence_enabled=True
)


def initialize_database():
    """Initialize the monitoring database."""
    logger.info("Monitoring database initialized")
    return monitoring_db
