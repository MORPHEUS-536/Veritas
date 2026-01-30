"""
Monitoring Logger and Database
Handles storage and retrieval of monitoring logs.
Uses PostgreSQL via NeonDB for persistent storage.
"""

import logging
import os
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy import create_engine, select, func, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

from app.models.schemas import MonitoringLog as MonitoringLogSchema, HealthStatus
from app.models.monitoring_models import MonitoringLog, MonitoringResult, SystemHealth, Base
from app.config import settings

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class MonitoringDatabase:
    """
    PostgreSQL database for monitoring logs with NeonDB backend.
    Provides the same interface as the in-memory version but with persistent storage.
    """
    
    def __init__(self, database_url: Optional[str] = None, max_entries: int = 10000):
        """
        Initialize the monitoring database connection.
        
        Args:
            database_url: PostgreSQL connection string (uses DATABASE_URL env var if not provided)
            max_entries: Maximum entries (kept for compatibility, not enforced in DB)
        """
        # Use provided URL or get from environment
        db_url = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:password@localhost:5432/veritas_db"
        )
        
        self.max_entries = max_entries
        
        try:
            # Create engine with NullPool for Neon (serverless) compatibility
            self.engine = create_engine(
                db_url,
                echo=settings.DEBUG,
                poolclass=NullPool,  # Neon recommends NullPool for serverless
                future=True
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                bind=self.engine,
                expire_on_commit=False,
                future=True
            )
            
            logger.info(f"PostgreSQL database connection initialized via NeonDB")
            
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL connection: {str(e)}")
            raise
    
    def initialize_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created/verified successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            raise
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def add_log(self, log_data: MonitoringLogSchema) -> str:
        """
        Add a monitoring log to the database.
        
        Args:
            log_data: MonitoringLogSchema to store
            
        Returns:
            Event ID
        """
        session = self.get_session()
        try:
            # Create MonitoringResult if provided
            result_obj = None
            if log_data.monitoring_result:
                result_obj = MonitoringResult(
                    status=log_data.monitoring_result.status,
                    analysis_result=log_data.monitoring_result.analysis_result,
                    timestamp=datetime.utcnow()
                )
                session.add(result_obj)
                session.flush()  # Get the ID before creating log
            
            # Create and store the log
            log_obj = MonitoringLog(
                event_id=log_data.event_id,
                source=log_data.source,
                component=log_data.component,
                message=log_data.message,
                monitoring_result_id=result_obj.id if result_obj else None,
                timestamp=log_data.timestamp or datetime.utcnow(),
                metadata=log_data.metadata
            )
            
            session.add(log_obj)
            session.commit()
            
            logger.debug(f"Log added: {log_data.event_id} - {log_data.source}")
            return log_data.event_id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to add log: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        source: Optional[str] = None,
        status: Optional[HealthStatus] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> tuple[List[MonitoringLogSchema], int]:
        """
        Query monitoring logs with filters.
        
        Args:
            limit: Maximum number of logs to return
            offset: Number of logs to skip
            source: Filter by data source
            status: Filter by health status
            start_time: Filter logs after this time
            end_time: Filter logs before this time
            
        Returns:
            Tuple of (filtered logs, total count)
        """
        session = self.get_session()
        try:
            # Build query
            query = select(MonitoringLog)
            filters = []
            
            # Apply filters
            if source:
                filters.append(MonitoringLog.source == source)
            
            if status:
                filters.append(MonitoringLog.monitoring_result.has(MonitoringResult.status == status))
            
            if start_time:
                filters.append(MonitoringLog.timestamp >= start_time)
            
            if end_time:
                filters.append(MonitoringLog.timestamp <= end_time)
            
            if filters:
                query = query.where(and_(*filters))
            
            # Get total count before pagination
            total_count = session.query(MonitoringLog).filter(and_(*filters) if filters else True).count()
            
            # Apply pagination
            results = session.execute(
                query.order_by(MonitoringLog.timestamp.desc())
                    .offset(offset)
                    .limit(limit)
            ).scalars().all()
            
            # Convert to schema objects (optional for compatibility)
            logger.debug(f"Query: returned {len(results)}/{total_count} logs")
            
            return results, total_count
            
        except Exception as e:
            logger.error(f"Failed to query logs: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_recent_logs(self, lookback_minutes: int = 10) -> List[MonitoringLog]:
        """Get logs from the last N minutes."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=lookback_minutes)
        logs, _ = self.get_logs(
            limit=self.max_entries,
            start_time=cutoff_time
        )
        return logs
    
    def get_log_by_id(self, event_id: str) -> Optional[MonitoringLog]:
        """Get a specific log by event ID."""
        session = self.get_session()
        try:
            result = session.execute(
                select(MonitoringLog).where(MonitoringLog.event_id == event_id)
            ).scalars().first()
            return result
        except Exception as e:
            logger.error(f"Failed to get log by ID: {str(e)}")
            return None
        finally:
            session.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored logs."""
        session = self.get_session()
        try:
            total_logs = session.query(func.count(MonitoringLog.event_id)).scalar() or 0
            
            if total_logs == 0:
                return {
                    "total_logs": 0,
                    "status_distribution": {
                        "NORMAL": 0,
                        "WARNING": 0,
                        "CRITICAL": 0,
                    },
                    "unique_sources": 0,
                }
            
            # Get status distribution
            status_dist = {}
            for status in HealthStatus:
                count = session.query(func.count(MonitoringLog.event_id)).join(
                    MonitoringResult
                ).filter(MonitoringResult.status == status).scalar() or 0
                status_dist[status.value] = count
            
            # Get unique sources
            unique_sources = session.query(func.count(func.distinct(MonitoringLog.source))).scalar() or 0
            
            # Get time range
            oldest_log = session.query(func.min(MonitoringLog.timestamp)).scalar()
            newest_log = session.query(func.max(MonitoringLog.timestamp)).scalar()
            
            return {
                "total_logs": total_logs,
                "status_distribution": status_dist,
                "unique_sources": unique_sources,
                "oldest_log": oldest_log.isoformat() if oldest_log else None,
                "newest_log": newest_log.isoformat() if newest_log else None,
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {str(e)}")
            return {}
        finally:
            session.close()
    
    def get_current_health_status(self) -> tuple[HealthStatus, float]:
        """
        Get the current overall system health status based on recent logs.
        
        Returns:
            Tuple of (status, average_severity)
        """
        session = self.get_session()
        try:
            # Get last 100 logs
            recent_logs = session.execute(
                select(MonitoringLog)
                .order_by(MonitoringLog.timestamp.desc())
                .limit(100)
            ).scalars().all()
            
            if not recent_logs:
                return HealthStatus.NORMAL, 0.0
            
            # Count statuses
            status_counts = {
                HealthStatus.NORMAL: 0,
                HealthStatus.WARNING: 0,
                HealthStatus.CRITICAL: 0,
            }
            
            for log in recent_logs:
                if log.monitoring_result:
                    status_counts[log.monitoring_result.status] += 1
            
            # Determine overall status (criticality order)
            if status_counts[HealthStatus.CRITICAL] > 0:
                return HealthStatus.CRITICAL, 0.8
            elif status_counts[HealthStatus.WARNING] > 0:
                return HealthStatus.WARNING, 0.5
            else:
                return HealthStatus.NORMAL, 0.2
                
        except Exception as e:
            logger.error(f"Failed to get health status: {str(e)}")
            return HealthStatus.NORMAL, 0.0
        finally:
            session.close()
    
    def clear_old_logs(self, older_than_minutes: int = 1440) -> int:
        """Remove logs older than specified minutes."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=older_than_minutes)
        
        session = self.get_session()
        try:
            # Delete old logs
            result = session.execute(
                select(MonitoringLog).where(MonitoringLog.timestamp < cutoff_time)
            )
            old_logs = result.scalars().all()
            removed_count = len(old_logs)
            
            for log in old_logs:
                session.delete(log)
            
            session.commit()
            
            if removed_count > 0:
                logger.info(f"Removed {removed_count} logs older than {older_than_minutes} minutes")
            
            return removed_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to clear old logs: {str(e)}")
            raise
        finally:
            session.close()


# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/veritas_db"
)

# Global database instance
monitoring_db = MonitoringDatabase(database_url=DATABASE_URL)


def initialize_database():
    """Initialize the monitoring database and create tables."""
    try:
        monitoring_db.initialize_tables()
        logger.info("Monitoring database initialized successfully")
        return monitoring_db
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
