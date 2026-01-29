"""
Data models and schemas for the Monitoring module.
Defines request/response structures and database models.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional, List
from pydantic import BaseModel, Field


class StatusEnum(str, Enum):
    """System health status levels"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"


class MonitoringDataRequest(BaseModel):
    """
    Schema for incoming data to be monitored.
    Contains the actual data and metadata about its source.
    """
    source_module: str = Field(..., description="Name of the module sending data (e.g., 'inference', 'preprocessing')")
    event_type: str = Field(..., description="Type of event (e.g., 'prediction_result', 'data_validation')")
    data: dict = Field(..., description="Actual data payload to monitor")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "source_module": "inference",
                "event_type": "prediction_result",
                "data": {
                    "prediction_score": 0.95,
                    "latency_ms": 250,
                    "model_version": "v2.1"
                },
                "metadata": {"user_id": "user_123"}
            }
        }


class MonitoringLog(BaseModel):
    """
    Represents a single monitoring log entry.
    Stored in memory or database for historical analysis.
    """
    log_id: str
    timestamp: datetime
    source_module: str
    event_type: str
    input_data_snapshot: dict
    detected_status: StatusEnum
    reason: str
    llm_analysis: Optional[str] = None
    llm_suggestions: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "log_id": "log_20260129_001",
                "timestamp": "2026-01-29T10:30:00Z",
                "source_module": "inference",
                "event_type": "prediction_result",
                "input_data_snapshot": {"prediction_score": 0.95},
                "detected_status": "normal",
                "reason": "Prediction score within expected range",
                "llm_analysis": "System performing normally with good prediction confidence",
                "llm_suggestions": ["Monitor next 10 predictions", "Log inference time"]
            }
        }


class MonitoringAnalysisRequest(BaseModel):
    """
    Request schema for manual LLM-based analysis.
    Allows users to trigger analysis on recent logs.
    """
    num_recent_logs: int = Field(default=10, ge=1, le=100, description="Number of recent logs to analyze")
    focus_area: Optional[str] = Field(default=None, description="Specific area to focus on (e.g., 'latency', 'accuracy')")

    class Config:
        json_schema_extra = {
            "example": {
                "num_recent_logs": 20,
                "focus_area": "latency"
            }
        }


class LLMAnalysisResult(BaseModel):
    """
    Result of LLM-based analysis.
    Contains the LLM's interpretation and recommendations.
    """
    system_state: StatusEnum = Field(..., description="Overall system state classification")
    analysis: str = Field(..., description="Detailed explanation of the system state")
    suggestions: List[str] = Field(..., description="Recommended corrective actions")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score of the analysis")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "system_state": "normal",
                "analysis": "System is performing optimally with consistent prediction quality",
                "suggestions": ["Continue current monitoring", "Log metrics hourly"],
                "confidence": 0.92,
                "analysis_timestamp": "2026-01-29T10:35:00Z"
            }
        }


class SystemHealthStatus(BaseModel):
    """
    Current system health snapshot.
    Returned by GET /monitor/status endpoint.
    """
    current_status: StatusEnum
    total_logs_processed: int
    warning_count: int
    critical_count: int
    last_update: datetime
    uptime_seconds: float
    last_critical_event: Optional[MonitoringLog] = None

    class Config:
        json_schema_extra = {
            "example": {
                "current_status": "normal",
                "total_logs_processed": 512,
                "warning_count": 3,
                "critical_count": 0,
                "last_update": "2026-01-29T10:35:00Z",
                "uptime_seconds": 3600.5,
                "last_critical_event": None
            }
        }


class MonitoringDataResponse(BaseModel):
    """
    Response schema for POST /monitor/data endpoint.
    Confirms receipt and provides immediate status.
    """
    success: bool
    message: str
    log_id: str
    detected_status: StatusEnum
    reason: str

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Data monitored successfully",
                "log_id": "log_20260129_001",
                "detected_status": "normal",
                "reason": "All metrics within acceptable range"
            }
        }


class LogsListResponse(BaseModel):
    """
    Response schema for GET /monitor/logs endpoint.
    Returns a paginated list of monitoring logs.
    """
    total_count: int
    returned_count: int
    logs: List[MonitoringLog]

    class Config:
        json_schema_extra = {
            "example": {
                "total_count": 512,
                "returned_count": 10,
                "logs": [
                    {
                        "log_id": "log_20260129_001",
                        "timestamp": "2026-01-29T10:30:00Z",
                        "source_module": "inference",
                        "event_type": "prediction_result",
                        "input_data_snapshot": {"prediction_score": 0.95},
                        "detected_status": "normal",
                        "reason": "Score within range",
                        "llm_analysis": None,
                        "llm_suggestions": None
                    }
                ]
            }
        }
