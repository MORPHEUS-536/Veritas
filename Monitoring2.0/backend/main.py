"""
Main Application Entry Point
FastAPI Monitoring System Backend
"""

import logging
import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.routes import router
from app.utils.database import initialize_database


# Configure logging
def setup_logging():
    """Configure application logging."""
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "formatter": "detailed",
                "class": "logging.FileHandler",
                "filename": settings.LOG_FILE,
            },
        },
        "loggers": {
            "app": {
                "handlers": ["default", "file"],
                "level": settings.LOG_LEVEL,
            },
        },
    }
    
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger("app")
    logger.info(f"Logging configured at level {settings.LOG_LEVEL}")
    return logger


# Setup logging
logger = setup_logging()


# Lifespan context manager for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown logic.
    """
    # Startup
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 60)
    
    # Validate configuration
    try:
        settings.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise
    
    # Initialize database
    initialize_database()
    logger.info("Database initialized")
    
    # Log feature flags
    logger.info(f"LLM Monitoring: {'ENABLED' if settings.ENABLE_LLM_MONITORING else 'DISABLED'}")
    logger.info(f"Warning Threshold: {settings.WARNING_THRESHOLD}")
    logger.info(f"Critical Threshold: {settings.CRITICAL_THRESHOLD}")
    
    logger.info(f"Application running on {settings.HOST}:{settings.PORT}")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info(f"Shutting down {settings.APP_NAME}")
    logger.info("=" * 60)


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Monitoring System Backend - Detects failures, anomalies, and system health using rule-based and LLM-assisted logic",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routes
app.include_router(router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "monitoring_api": "/api/v1/monitoring",
        }
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and orchestration systems."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        },
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server at {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
