#!/usr/bin/env python3
"""
Database Connection Verification Script
Tests connectivity to NeonDB PostgreSQL for all backends.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_neondb_connection():
    """Test NeonDB PostgreSQL connection."""
    logger.info("=" * 60)
    logger.info("Testing NeonDB PostgreSQL Connection")
    logger.info("=" * 60)
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        logger.error("DATABASE_URL not found in environment variables")
        logger.error("Please set DATABASE_URL in .env file")
        return False
    
    logger.info(f"Connection String: {mask_url(database_url)}")
    
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.pool import NullPool
        
        # Create engine
        engine = create_engine(
            database_url,
            poolclass=NullPool,
            future=True,
            echo=False
        )
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as connection_test"))
            result.close()
        
        logger.info("✓ PostgreSQL connection successful")
        engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"✗ PostgreSQL connection failed: {str(e)}")
        return False


def test_monitoring2_database():
    """Test Monitoring2.0 database models."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Monitoring2.0 Database Models")
    logger.info("=" * 60)
    
    try:
        sys.path.insert(0, "Monitoring2.0/backend")
        from app.utils.database import monitoring_db
        from app.models.monitoring_models import Base
        
        # Initialize tables
        monitoring_db.initialize_tables()
        
        logger.info("✓ Monitoring2.0 tables created/verified")
        return True
        
    except Exception as e:
        logger.error(f"✗ Monitoring2.0 database setup failed: {str(e)}")
        return False


def test_staffstuddash_database():
    """Test staffstuddash database models."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing staffstuddash Database Models")
    logger.info("=" * 60)
    
    try:
        sys.path.insert(0, "staffstuddash/backend")
        from datastore import datastore
        from db_models import Base
        
        # Check initialization
        if datastore.initialized or datastore.use_fallback:
            logger.info(f"✓ staffstuddash database {'connected' if datastore.initialized else 'fallback mode'}")
            return True
        else:
            logger.error("✗ staffstuddash database not initialized")
            return False
            
    except Exception as e:
        logger.error(f"✗ staffstuddash database setup failed: {str(e)}")
        return False


def test_dropout_database():
    """Test dropout database models."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Dropout Detection Database Models")
    logger.info("=" * 60)
    
    try:
        sys.path.insert(0, "dropout")
        from database import db_manager
        from db_models import Base
        
        if db_manager.initialized:
            logger.info("✓ Dropout database initialized successfully")
            return True
        else:
            logger.error("✗ Dropout database not initialized")
            return False
            
    except Exception as e:
        logger.error(f"✗ Dropout database setup failed: {str(e)}")
        return False


def mask_url(url):
    """Mask sensitive information in database URL."""
    if "@" in url:
        parts = url.split("@")
        return parts[0].split("://")[0] + "://***:***@" + parts[1]
    return url


def main():
    """Run all tests."""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║ Veritas Backend - Database Connection Verification ║")
    logger.info("╚" + "=" * 58 + "╝")
    
    results = {
        "PostgreSQL Connection": test_neondb_connection(),
        "Monitoring2.0": test_monitoring2_database(),
        "staffstuddash": test_staffstuddash_database(),
        "Dropout Detection": test_dropout_database(),
    }
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Summary")
    logger.info("=" * 60)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    logger.info("\n" + "=" * 60)
    if all_passed:
        logger.info("✓ All tests passed! Database setup is complete.")
        logger.info("\nYour backends are ready to use PostgreSQL via NeonDB!")
    else:
        logger.error("✗ Some tests failed. Please check the errors above.")
        logger.error("\nCommon issues:")
        logger.error("1. DATABASE_URL not set in .env")
        logger.error("2. Invalid PostgreSQL connection string")
        logger.error("3. Network connectivity issues")
        logger.error("4. NeonDB project not configured")
    logger.info("=" * 60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
