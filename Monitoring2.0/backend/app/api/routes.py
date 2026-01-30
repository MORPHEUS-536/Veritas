"""
FastAPI API Routes for Monitoring System
Exposes endpoints for event submission, health status, logs retrieval, and LLM analysis.
"""

import logging
import uuid
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from app.models import (
    EventRequest,
    MonitoringLog,
    HealthStatusResponse,
    LogQueryRequest,
    LogsResponse,
    LLMAnalysisRequest,
    LLMAnalysisResponse,
    ErrorResponse,
    HealthStatus,
)
from app.monitoring.engine import MonitoringEngine
from app.services.groq_service import GroqLLMService
from app.utils.database import monitoring_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])

# Global instances
monitoring_engine = MonitoringEngine(
    warning_threshold=0.7,
    critical_threshold=0.9
)
llm_service = GroqLLMService()


@router.post("/events", response_model=MonitoringLog, status_code=201)
async def submit_event(request: EventRequest) -> MonitoringLog:
    """
    Submit a data/event for monitoring analysis.
    
    The system will:
    1. Analyze the event using rule-based monitoring
    2. Store the monitoring log
    3. Optionally trigger LLM analysis based on severity
    
    Args:
        request: EventRequest containing source, event_type, and data
        
    Returns:
        MonitoringLog with analysis results
        
    Example:
        POST /api/v1/monitoring/events
        {
            "source": "api_module",
            "event_type": "api_response",
            "data": {"response_time": 250, "status_code": 200},
            "metadata": {"user_id": "123"}
        }
    """
    try:
        # Generate unique event ID
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        
        logger.info(f"Processing event {event_id} from {request.source}")
        
        # Analyze event using rule-based monitoring
        monitoring_result = monitoring_engine.analyze(
            source=request.source,
            event_type=request.event_type,
            data=request.data
        )
        
        # Create monitoring log entry
        log_entry = MonitoringLog(
            event_id=event_id,
            source=request.source,
            event_type=request.event_type,
            input_snapshot=request.data,
            monitoring_result=monitoring_result,
            timestamp=datetime.utcnow()
        )
        
        # Store in database
        monitoring_db.add_log(log_entry)
        
        logger.info(
            f"Event {event_id} analyzed: {monitoring_result.status.value} "
            f"(severity: {monitoring_result.severity_score})"
        )
        
        return log_entry
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing event: {str(e)}"
        )


@router.get("/health", response_model=HealthStatusResponse)
async def get_health_status() -> HealthStatusResponse:
    """
    Get current system health status.
    
    Returns the overall system health based on recent monitoring logs.
    
    Returns:
        HealthStatusResponse with current status and statistics
        
    Example:
        GET /api/v1/monitoring/health
    """
    try:
        current_status, avg_severity = monitoring_db.get_current_health_status()
        stats = monitoring_db.get_statistics()
        
        # Get recent issues
        recent_logs, _ = monitoring_db.get_logs(limit=100)
        recent_issues = []
        for log in recent_logs:
            if log.monitoring_result.detected_issues:
                recent_issues.extend(log.monitoring_result.detected_issues)
        
        # Deduplicate and limit
        recent_issues = list(set(recent_issues))[:5]
        
        response = HealthStatusResponse(
            current_status=current_status,
            severity_score=avg_severity,
            last_update=datetime.utcnow(),
            recent_issues=recent_issues,
            total_events_processed=stats.get("total_logs", 0)
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting health status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting health status: {str(e)}"
        )


@router.post("/logs/query", response_model=LogsResponse)
async def query_logs(request: LogQueryRequest) -> LogsResponse:
    """
    Query monitoring logs with filtering and pagination.
    
    Args:
        request: LogQueryRequest with filters and pagination parameters
        
    Returns:
        LogsResponse with matching logs and total count
        
    Example:
        POST /api/v1/monitoring/logs/query
        {
            "limit": 50,
            "offset": 0,
            "status": "WARNING",
            "source": "api_module"
        }
    """
    try:
        logs, total_count = monitoring_db.get_logs(
            limit=request.limit,
            offset=request.offset,
            source=request.source,
            status=request.status,
            start_time=request.start_time,
            end_time=request.end_time,
        )
        
        response = LogsResponse(
            logs=logs,
            total_count=total_count,
            returned_count=len(logs)
        )
        
        logger.info(f"Query returned {len(logs)}/{total_count} logs")
        
        return response
        
    except Exception as e:
        logger.error(f"Error querying logs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error querying logs: {str(e)}"
        )


@router.get("/logs", response_model=LogsResponse)
async def get_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    source: Optional[str] = None,
    status: Optional[HealthStatus] = None,
) -> LogsResponse:
    """
    Get monitoring logs with optional filtering.
    
    Query parameters:
        limit: Number of logs to return (default 100)
        offset: Number of logs to skip (default 0)
        source: Filter by data source
        status: Filter by health status (NORMAL, WARNING, CRITICAL)
        
    Returns:
        LogsResponse with logs and total count
        
    Example:
        GET /api/v1/monitoring/logs?limit=50&status=WARNING
    """
    try:
        logs, total_count = monitoring_db.get_logs(
            limit=limit,
            offset=offset,
            source=source,
            status=status,
        )
        
        response = LogsResponse(
            logs=logs,
            total_count=total_count,
            returned_count=len(logs)
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting logs: {str(e)}"
        )


@router.post("/analysis/llm", response_model=dict)
async def trigger_llm_analysis(request: LLMAnalysisRequest) -> dict:
    """
    Manually trigger LLM-based analysis of recent logs.
    
    The LLM will analyze recent monitoring data and provide:
    - Explanation of anomalies
    - Severity classification
    - Recommended actions
    
    Args:
        request: LLMAnalysisRequest with lookback period and focus areas
        
    Returns:
        Dictionary with analysis, severity, findings, and recommendations
        
    Example:
        POST /api/v1/monitoring/analysis/llm
        {
            "lookback_minutes": 30,
            "focus_areas": ["response_times", "error_rates"]
        }
    """
    try:
        if not llm_service.enabled:
            raise HTTPException(
                status_code=503,
                detail="LLM analysis is not enabled. Set ENABLE_LLM_MONITORING=True and provide GROQ_API_KEY."
            )
        
        # Get recent logs
        recent_logs = monitoring_db.get_recent_logs(request.lookback_minutes)
        
        if not recent_logs:
            raise HTTPException(
                status_code=400,
                detail=f"No logs found in the last {request.lookback_minutes} minutes"
            )
        
        logger.info(f"Triggering LLM analysis on {len(recent_logs)} recent logs")
        
        # Call LLM service
        analysis = await llm_service.analyze_logs(recent_logs, request.focus_areas)
        
        logger.info(f"LLM analysis completed with severity: {analysis.get('severity')}")
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during LLM analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error during LLM analysis: {str(e)}"
        )


@router.get("/stats", response_model=dict)
async def get_statistics() -> dict:
    """
    Get statistics about monitoring data.
    
    Returns:
        Dictionary with log counts, status distribution, and other statistics
        
    Example:
        GET /api/v1/monitoring/stats
    """
    try:
        stats = monitoring_db.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting statistics: {str(e)}"
        )


@router.post("/analysis/re-evaluate")
async def re_evaluate_recent_logs(
    lookback_minutes: int = Query(60, ge=1, le=1440)
) -> dict:
    """
    Manually trigger re-evaluation of recent logs.
    Useful for testing and manual trigger scenarios.
    
    Args:
        lookback_minutes: How many minutes back to re-evaluate
        
    Returns:
        Dictionary with re-evaluation summary
        
    Example:
        POST /api/v1/monitoring/analysis/re-evaluate?lookback_minutes=30
    """
    try:
        recent_logs = monitoring_db.get_recent_logs(lookback_minutes)
        
        if not recent_logs:
            return {
                "message": f"No logs found in the last {lookback_minutes} minutes",
                "re_evaluated_count": 0
            }
        
        # Count issues
        critical_count = sum(
            1 for log in recent_logs
            if log.monitoring_result.status == HealthStatus.CRITICAL
        )
        warning_count = sum(
            1 for log in recent_logs
            if log.monitoring_result.status == HealthStatus.WARNING
        )
        normal_count = sum(
            1 for log in recent_logs
            if log.monitoring_result.status == HealthStatus.NORMAL
        )
        
        logger.info(
            f"Re-evaluation completed: {critical_count} critical, "
            f"{warning_count} warning, {normal_count} normal"
        )
        
        return {
            "message": f"Re-evaluated {len(recent_logs)} logs from last {lookback_minutes} minutes",
            "re_evaluated_count": len(recent_logs),
            "summary": {
                "critical": critical_count,
                "warning": warning_count,
                "normal": normal_count,
            }
        }
        
    except Exception as e:
        logger.error(f"Error during re-evaluation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error during re-evaluation: {str(e)}"
        )


@router.post("/maintenance/cleanup")
async def cleanup_old_logs(older_than_hours: int = Query(24, ge=1, le=720)) -> dict:
    """
    Remove monitoring logs older than specified hours.
    
    Args:
        older_than_hours: Remove logs older than this many hours
        
    Returns:
        Dictionary with cleanup summary
        
    Example:
        POST /api/v1/monitoring/maintenance/cleanup?older_than_hours=48
    """
    try:
        removed_count = monitoring_db.clear_old_logs(older_than_minutes=older_than_hours * 60)
        
        logger.info(f"Cleanup completed: removed {removed_count} logs")
        
        return {
            "message": f"Removed {removed_count} logs older than {older_than_hours} hours",
            "removed_count": removed_count
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error during cleanup: {str(e)}"
        )


@router.get("/", response_model=dict)
async def monitoring_root() -> dict:
    """
    Root endpoint for monitoring API.
    Returns information about available endpoints and system status.
    
    Example:
        GET /api/v1/monitoring/
    """
    return {
        "service": "Monitoring System",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "events": {
                "POST /events": "Submit data/event for monitoring",
            },
            "status": {
                "GET /health": "Get current system health status",
                "GET /stats": "Get monitoring statistics",
            },
            "logs": {
                "GET /logs": "Query monitoring logs with filters",
                "POST /logs/query": "Advanced log query with filters",
            },
            "analysis": {
                "POST /analysis/llm": "Trigger LLM-based analysis",
                "POST /analysis/re-evaluate": "Re-evaluate recent logs",
            },
            "maintenance": {
                "POST /maintenance/cleanup": "Remove old logs",
            }
        }
    }


def create_routes():
    """Factory function to create and return the router."""
    return router
