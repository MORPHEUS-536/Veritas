"""
Configuration Management for Monitoring System
Loads settings from environment variables with sensible defaults.
Supports PostgreSQL via NeonDB for cloud database hosting.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=str(env_path))


class Settings:
    """Application settings loaded from environment variables."""
    
    # FastAPI Configuration
    APP_NAME: str = "Monitoring System Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database Configuration (PostgreSQL via NeonDB)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/veritas_db"
    )
    
    # Monitoring Configuration
    ENABLE_LLM_MONITORING: bool = os.getenv("ENABLE_LLM_MONITORING", "True").lower() == "true"
    WARNING_THRESHOLD: float = float(os.getenv("WARNING_THRESHOLD", "0.7"))
    CRITICAL_THRESHOLD: float = float(os.getenv("CRITICAL_THRESHOLD", "0.9"))
    
    # Groq API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
    GROQ_MAX_TOKENS: int = int(os.getenv("GROQ_MAX_TOKENS", "1024"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/monitoring.log")
    
    # Data Retention
    MAX_LOG_ENTRIES: int = int(os.getenv("MAX_LOG_ENTRIES", "10000"))
    
    @classmethod
    def validate(cls):
        """Validate critical configuration settings."""
        if cls.ENABLE_LLM_MONITORING and not cls.GROQ_API_KEY:
            raise ValueError(
                "ENABLE_LLM_MONITORING is True but GROQ_API_KEY is not set. "
                "Please set GROQ_API_KEY in environment or .env file."
            )
        
        if cls.WARNING_THRESHOLD >= cls.CRITICAL_THRESHOLD:
            raise ValueError(
                f"WARNING_THRESHOLD ({cls.WARNING_THRESHOLD}) must be less than "
                f"CRITICAL_THRESHOLD ({cls.CRITICAL_THRESHOLD})"
            )
    
    def __repr__(self):
        return f"Settings(APP_NAME={self.APP_NAME}, DEBUG={self.DEBUG}, ENABLE_LLM_MONITORING={self.ENABLE_LLM_MONITORING})"


# Global settings instance
settings = Settings()
