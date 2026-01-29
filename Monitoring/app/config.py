"""
Configuration settings for the Monitoring module.
Reads from environment variables with sensible defaults.
"""

import os
from typing import Literal

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# Monitoring Configuration
MAX_LOGS_STORED = int(os.getenv("MAX_LOGS_STORED", 1000))
MONITORING_CHECK_INTERVAL = int(os.getenv("MONITORING_CHECK_INTERVAL", 60))  # seconds

# Thresholds for anomaly detection
ANOMALY_THRESHOLD_WARNING = float(os.getenv("ANOMALY_THRESHOLD_WARNING", 0.7))
ANOMALY_THRESHOLD_CRITICAL = float(os.getenv("ANOMALY_THRESHOLD_CRITICAL", 0.9))

# LLM Configuration
ENABLE_LLM_MONITORING = os.getenv("ENABLE_LLM_MONITORING", "false").lower() == "true"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # openai, claude, gemini
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 500))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/monitoring.log")

# Validation on startup
if ENABLE_LLM_MONITORING and not LLM_API_KEY:
    raise ValueError(
        "ENABLE_LLM_MONITORING is True but LLM_API_KEY is not set. "
        "Provide an API key in .env file or disable LLM monitoring."
    )

# System health check
HEALTH_CHECK_ENABLED = os.getenv("HEALTH_CHECK_ENABLED", "true").lower() == "true"
HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 30))  # seconds
