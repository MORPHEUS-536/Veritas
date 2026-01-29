"""
PostgreSQL database connection and session management.
Provides SQLAlchemy engine, session factory, and connection pooling.
Supports Neon DB as primary database.

Neon DB Setup:
1. Go to https://console.neon.tech
2. Create a project
3. Copy connection string from "Connection string" tab
4. Set DATABASE_URL environment variable:
   DATABASE_URL=postgresql://<user>:<password>@<host>/veritas_db?sslmode=require
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool
import os
from typing import Generator

# Database URL from environment or Neon default
# For Neon DB: postgresql://user:password@host/database?sslmode=require
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/veritas_db"
)

# Validate database URL format
if not DATABASE_URL or "postgresql" not in DATABASE_URL:
    raise ValueError(
        "DATABASE_URL must be set and contain 'postgresql://'\n"
        "For Neon: postgresql://user:password@host/database?sslmode=require"
    )

# Create engine with connection pooling and optimizations
# Neon DB: Uses pgBouncer connection pooling
# Recommended: pool_size=5-10 for serverless, higher for dedicated
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,              # Neon: start with 5, scale as needed
    max_overflow=10,          # Neon: additional on-demand connections
    pool_pre_ping=True,       # Verify connections before using (important for serverless)
    echo=False,               # Set to True for SQL debugging
    connect_args={
        "connect_timeout": 10,
        # Note: statement_timeout not supported by Neon's pgBouncer pooler
        "application_name": "veritas_backend"
    }
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Base class for all ORM models
Base = declarative_base()


# Enable UUID extension on PostgreSQL
@event.listens_for(engine, "connect")
def enable_uuid_extension(dbapi_conn, connection_record):
    """Enable UUID extension when connection is created."""
    with dbapi_conn.cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
        dbapi_conn.commit()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI endpoints to get DB session.
    Usage:
        @app.get("/students")
        async def get_students(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables defined in Base metadata."""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all tables. Use with caution."""
    Base.metadata.drop_all(bind=engine)


def reset_sequences():
    """Reset all sequences in database."""
    db = SessionLocal()
    try:
        # This resets autoincrement sequences
        db.execute(text("""
            SELECT setval(pg_get_serial_sequence(t.tablename, 'id'), 1)
            FROM pg_tables t
            WHERE t.schemaname != 'pg_catalog'
            AND t.schemaname != 'information_schema'
        """))
        db.commit()
    finally:
        db.close()
