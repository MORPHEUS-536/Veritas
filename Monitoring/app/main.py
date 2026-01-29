"""
Main FastAPI application for the Monitoring module.
Entry point for the monitoring service.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

from app.config import DEBUG_MODE, API_HOST, API_PORT
from app.routers import monitoring
from app.utils.logger import logger


# Create FastAPI app instance
app = FastAPI(
    title="Monitoring Module API",
    description="Backend monitoring service for hackathon application. Detects anomalies, threshold violations, and suspicious patterns. Integrates LLM for intelligent analysis.",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Configure CORS (allow requests from other modules)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(monitoring.router)


@app.on_event("startup")
async def startup_event():
    """Startup event - initialize services"""
    logger.info("=" * 60)
    logger.info("Monitoring Module Starting Up")
    logger.info("=" * 60)
    logger.info(f"Debug Mode: {DEBUG_MODE}")
    logger.info(f"API: http://{API_HOST}:{API_PORT}")
    logger.info(f"Docs: http://{API_HOST}:{API_PORT}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event - cleanup"""
    logger.info("=" * 60)
    logger.info("Monitoring Module Shutting Down")
    logger.info("=" * 60)


@app.get(
    "/",
    summary="Root endpoint",
    description="Welcome message and service information"
)
async def root():
    """
    Root endpoint providing service information.
    
    Returns:
        Service welcome message and documentation links
    """
    return {
        "message": "Welcome to Monitoring Module API",
        "service": "Monitoring",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "documentation": "/docs",
        "endpoints": {
            "submit_data": "POST /monitor/data",
            "get_status": "GET /monitor/status",
            "get_logs": "GET /monitor/logs",
            "llm_analysis": "POST /monitor/analyze",
            "health_check": "GET /monitor/health"
        }
    }


@app.get("/health", summary="Service health check")
async def health():
    """
    Service health check endpoint.
    
    Returns:
        200 OK with health status
    """
    return {
        "status": "healthy",
        "service": "monitoring",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for uncaught errors.
    
    Args:
        request: Request that caused the error
        exc: The exception
        
    Returns:
        JSON error response
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if DEBUG_MODE else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run the FastAPI application
    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=DEBUG_MODE,
        log_level="info"
    )
