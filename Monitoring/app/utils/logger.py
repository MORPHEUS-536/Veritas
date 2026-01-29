"""
Logging utility for the Monitoring module.
Provides structured logging with file and console output.
"""

import logging
import os
from pathlib import Path
from app.config import LOG_LEVEL, LOG_FILE


def setup_logger(name: str = "monitoring") -> logging.Logger:
    """
    Configure and return a logger instance with both file and console handlers.
    
    Args:
        name: Name of the logger
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Prevent duplicate handlers
    if logger.hasHandlers():
        return logger
    
    # Format for log messages
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (DEBUG and above)
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# Create a module-level logger
logger = setup_logger()
