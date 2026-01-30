"""
Data Models and Schemas for Monitoring System
Defines Pydantic models for type safety and validation.
"""

from enum import Enum
from datetime import datetime
from typing import Any, Optional, Dict, List
from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    """System health status levels."""
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class FailSafeAction(str, Enum):
    """Fail-safe decision actions."""
    CONTINUE = "CONTINUE"
    RETRY = "RETRY"
    REPROCESS = "REPROCESS"
    ESCALATE = "ESCALATE"
    HALT = "HALT"


class EventRequest(BaseModel):
    """Request model for submitting data/events for monitoring."""
    source: str = Field(..., description="Data source or module name")
    event_type: str = Field(..., description="Type of event (e.g., 'api_response', 'database_query')")
    data: Dict[str, Any] = Field(..., description="Event data payload")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "source": "api_module",
                "event_type": "api_response",
                "data": {"response_time": 250, "status_code": 200, "output": "success"},
                "metadata": {"user_id": "123"}
            }
        }


class MonitoringResult(BaseModel):
    """Result of monitoring analysis for a single event."""
    status: HealthStatus = Field(..., description="System health status")
    severity_score: float = Field(..., ge=0, le=1, description="Severity score from 0.0 to 1.0")
    reasoning: str = Field(..., description="Human-readable explanation of the status")
    detected_issues: List[str] = Field(default_factory=list, description="List of detected issues")
    suggestions: List[str] = Field(default_factory=list, description="Suggested actions")
    failed_rules: List[str] = Field(default_factory=list, description="Rules that triggered")


class MonitoringLog(BaseModel):
    """Complete monitoring log entry."""
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the event was monitored")
    event_id: str = Field(..., description="Unique identifier for the event")
    source: str = Field(..., description="Data source or module")
    event_type: str = Field(..., description="Type of event")
    input_snapshot: Dict[str, Any] = Field(..., description="Snapshot of input data")
    monitoring_result: MonitoringResult = Field(..., description="Monitoring analysis result")
    llm_analysis: Optional[Dict[str, Any]] = Field(default=None, description="Optional LLM analysis output")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-01-30T10:30:00Z",
                "event_id": "evt_123abc",
                "source": "api_module",
                "event_type": "api_response",
                "input_snapshot": {"response_time": 250, "status_code": 200},
                "monitoring_result": {
                    "status": "NORMAL",
                    "severity_score": 0.2,
                    "reasoning": "Response time is within acceptable range",
                    "detected_issues": [],
                    "suggestions": [],
                    "failed_rules": []
                }
            }
        }


class HealthStatusResponse(BaseModel):
    """Response model for current system health status."""
    current_status: HealthStatus = Field(..., description="Current overall system health status")
    severity_score: float = Field(..., ge=0, le=1, description="Overall severity score")
    last_update: datetime = Field(..., description="When status was last updated")
    recent_issues: List[str] = Field(default_factory=list, description="Recent detected issues")
    total_events_processed: int = Field(..., description="Total number of events processed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_status": "NORMAL",
                "severity_score": 0.3,
                "last_update": "2025-01-30T10:35:00Z",
                "recent_issues": [],
                "total_events_processed": 150
            }
        }


class LogQueryRequest(BaseModel):
    """Request model for querying monitoring logs."""
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of logs to return")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")
    source: Optional[str] = Field(default=None, description="Filter by source")
    status: Optional[HealthStatus] = Field(default=None, description="Filter by health status")
    start_time: Optional[datetime] = Field(default=None, description="Filter logs after this time")
    end_time: Optional[datetime] = Field(default=None, description="Filter logs before this time")


class LogsResponse(BaseModel):
    """Response model for logs query."""
    logs: List[MonitoringLog] = Field(..., description="List of monitoring logs")
    total_count: int = Field(..., description="Total number of logs matching query")
    returned_count: int = Field(..., description="Number of logs in this response")


class LLMAnalysisRequest(BaseModel):
    """Request model for LLM-based analysis."""
    lookback_minutes: int = Field(default=10, ge=1, le=1440, description="Minutes of logs to analyze")
    focus_areas: Optional[List[str]] = Field(default=None, description="Specific areas to focus on")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lookback_minutes": 30,
                "focus_areas": ["api_response_times", "database_queries"]
            }
        }


class LLMAnalysisResponse(BaseModel):
    """Response model for LLM analysis."""
    analysis: str = Field(..., description="LLM-generated analysis of patterns and anomalies")
    severity: HealthStatus = Field(..., description="LLM's severity classification")
    key_findings: List[str] = Field(..., description="Key findings from LLM analysis")
    recommendations: List[str] = Field(..., description="Recommended actions")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level of the analysis")


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When error occurred")
