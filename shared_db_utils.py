"""
PostgreSQL Database Connection and Session Management
Uses NeonDB for cloud PostgreSQL hosting.
Provides SQLAlchemy session management for all backends.
"""

import os
import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


# Database URL from environment or default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/veritas_db"
)


class DatabaseManager:
    """
    Manages PostgreSQL database connections using SQLAlchemy.
    Supports both NeonDB (cloud) and local PostgreSQL instances.
    """

    def __init__(self, database_url: str = DATABASE_URL):
        """
        Initialize database connection.

        Args:
            database_url: PostgreSQL connection string
        """
        self.database_url = database_url
        
        # Create engine with NullPool for Neon (serverless) compatibility
        self.engine = create_engine(
            database_url,
            echo=os.getenv("DEBUG", "False").lower() == "true",
            poolclass=NullPool,  # Neon recommends NullPool for serverless
            future=True
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            future=True
        )
        
        logger.info(f"Database connection initialized: {self._mask_url(database_url)}")

    def _mask_url(self, url: str) -> str:
        """Mask sensitive information in database URL for logging."""
        if "@" in url:
            parts = url.split("@")
            return parts[0].split("://")[0] + "://***:***@" + parts[1]
        return url

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope for database operations.
        
        Usage:
            with db_manager.session_scope() as session:
                # perform database operations
                session.add(obj)
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def initialize_database(self):
        """Initialize database tables and schema."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                conn.commit()
            logger.info("Database connection verified successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise

    def create_tables(self, base):
        """
        Create all tables from SQLAlchemy Base.
        
        Args:
            base: SQLAlchemy declarative base (e.g., from sqlalchemy.orm import declarative_base)
        """
        try:
            base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            raise

    def close(self):
        """Close database connection."""
        self.engine.dispose()
        logger.info("Database connection closed")


# Global database manager instance
db_manager = DatabaseManager()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to inject database sessions.
    
    Usage in FastAPI routes:
        @app.get("/")
        def get_data(db: Session = Depends(get_db)):
            # use db
    """
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()
