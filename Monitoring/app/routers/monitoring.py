"""
Monitoring API Router
Defines REST endpoints for the monitoring module.
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from app.models.schemas import (
    MonitoringDataRequest,
    MonitoringDataResponse,
    MonitoringAnalysisRequest,
    SystemHealthStatus,
    LogsListResponse,
    StatusEnum,
    LLMAnalysisResult
)
from app.services.monitoring_service import monitoring_service
from app.services.llm_service import llm_service
from app.utils.logger import logger


router = APIRouter(
    prefix="/monitor",
    tags=["monitoring"],
    responses={500: {"description": "Internal server error"}}
)


@router.post(
    "/data",
    response_model=MonitoringDataResponse,
    summary="Submit data for monitoring",
    description="Accepts data/events from other modules to monitor for anomalies"
)
async def submit_monitoring_data(request: MonitoringDataRequest) -> MonitoringDataResponse:
    """
    Submit data to the monitoring service.
    
    The service will:
    1. Check for anomalies using rule-based detection
    2. Classify status (normal/warning/critical)
    3. Optionally run LLM analysis for non-normal events
    4. Store logs for historical analysis
    
    Args:
        request: MonitoringDataRequest with data to monitor
        
    Returns:
        MonitoringDataResponse with detection result
        
    Example:
        ```json
        {
            "source_module": "inference",
            "event_type": "prediction_result",
            "data": {
                "prediction_score": 0.95,
                "latency_ms": 250
            }
        }
        ```
    """
    try:
        log, message = await monitoring_service.process_data(request)
        
        return MonitoringDataResponse(
            success=True,
            message=message,
            log_id=log.log_id,
            detected_status=log.detected_status,
            reason=log.reason
        )
        
    except Exception as e:
        logger.error(f"Error processing monitoring data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing data: {str(e)}"
        )


@router.get(
    "/status",
    response_model=SystemHealthStatus,
    summary="Get current system health",
    description="Returns the current overall system health status and metrics"
)
async def get_system_status() -> SystemHealthStatus:
    """
    Get the current system health status.
    
    Returns:
        SystemHealthStatus with current metrics and status
        
    Example Response:
        ```json
        {
            "current_status": "normal",
            "total_logs_processed": 512,
            "warning_count": 3,
            "critical_count": 0,
            "last_update": "2026-01-29T10:35:00Z",
            "uptime_seconds": 3600.5,
            "last_critical_event": null
        }
        ```
    """
    try:
        health = monitoring_service.get_system_health()
        
        return SystemHealthStatus(
            current_status=health["current_status"],
            total_logs_processed=health["total_logs_processed"],
            warning_count=health["warning_count"],
            critical_count=health["critical_count"],
            last_update=health["last_update"],
            uptime_seconds=health["uptime_seconds"],
            last_critical_event=health["last_critical_event"]
        )
        
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving status: {str(e)}"
        )


@router.get(
    "/logs",
    response_model=LogsListResponse,
    summary="Get recent monitoring logs",
    description="Returns recent monitoring logs with optional filtering"
)
async def get_monitoring_logs(
    limit: int = Query(default=50, ge=1, le=500, description="Number of recent logs to return"),
    status: str = Query(default=None, description="Filter by status: normal, warning, or critical"),
    source: str = Query(default=None, description="Filter by source module name")
) -> LogsListResponse:
    """
    Retrieve recent monitoring logs with optional filtering.
    
    Args:
        limit: Number of recent logs (1-500, default: 50)
        status: Filter by status (normal/warning/critical)
        source: Filter by source module
        
    Returns:
        LogsListResponse with list of matching logs
        
    Example:
        GET /monitor/logs?limit=20&status=warning
        
    Example Response:
        ```json
        {
            "total_count": 512,
            "returned_count": 5,
            "logs": [
                {
                    "log_id": "log_20260129_001",
                    "timestamp": "2026-01-29T10:30:00Z",
                    "source_module": "inference",
                    "event_type": "prediction_result",
                    "input_data_snapshot": {"prediction_score": 0.95},
                    "detected_status": "normal",
                    "reason": "Score within range",
                    "llm_analysis": null,
                    "llm_suggestions": null
                }
            ]
        }
        ```
    """
    try:
        # Fetch logs based on filters
        if status:
            try:
                status_enum = StatusEnum(status.lower())
                logs = monitoring_service.get_logs_by_status(status_enum, limit)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status '{status}'. Must be: normal, warning, or critical"
                )
        elif source:
            logs = monitoring_service.get_logs_by_source(source, limit)
        else:
            logs = monitoring_service.get_recent_logs(limit)
        
        return LogsListResponse(
            total_count=len(monitoring_service.logs),
            returned_count=len(logs),
            logs=logs
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving logs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving logs: {str(e)}"
        )


@router.post(
    "/analyze",
    response_model=LLMAnalysisResult,
    summary="Trigger LLM-based analysis",
    description="Manually trigger intelligent LLM analysis on recent logs"
)
async def trigger_llm_analysis(
    request: MonitoringAnalysisRequest
) -> LLMAnalysisResult:
    """
    Manually trigger LLM-based intelligent analysis on recent monitoring logs.
    
    The LLM will:
    1. Analyze recent log patterns
    2. Classify system state (normal/warning/critical)
    3. Provide human-readable explanations
    4. Suggest corrective actions
    
    Args:
        request: MonitoringAnalysisRequest with analysis parameters
        
    Returns:
        LLMAnalysisResult with classification and suggestions
        
    Example:
        ```json
        {
            "num_recent_logs": 20,
            "focus_area": "latency"
        }
        ```
        
    Example Response:
        ```json
        {
            "system_state": "warning",
            "analysis": "System is experiencing higher than normal latency...",
            "suggestions": [
                "Check inference pipeline",
                "Review resource utilization",
                "Consider load balancing"
            ],
            "confidence": 0.92,
            "analysis_timestamp": "2026-01-29T10:35:00Z"
        }
        ```
    """
    if not llm_service.enabled:
        raise HTTPException(
            status_code=503,
            detail="LLM monitoring is not enabled. Set ENABLE_LLM_MONITORING=true in .env"
        )
    
    try:
        # Get recent logs
        recent_logs = monitoring_service.get_recent_logs(request.num_recent_logs)
        
        if not recent_logs:
            raise HTTPException(
                status_code=400,
                detail="No logs available for analysis"
            )
        
        # Trigger LLM analysis
        analysis = await llm_service.analyze_logs(recent_logs, request.focus_area)
        
        if analysis is None:
            raise HTTPException(
                status_code=503,
                detail="LLM analysis failed. Check API key and provider configuration."
            )
        
        logger.info(f"LLM analysis completed: {analysis.system_state.value}")
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during LLM analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error performing analysis: {str(e)}"
        )


# Health check endpoint
@router.get(
    "/health",
    summary="Health check",
    description="Simple health check endpoint for the monitoring module"
)
async def health_check():
    """
    Simple health check for the monitoring module.
    
    Returns:
        200 OK if service is running
    """
    return {
        "status": "healthy",
        "service": "monitoring",
        "timestamp": datetime.utcnow().isoformat(),
        "llm_enabled": llm_service.enabled
    }
