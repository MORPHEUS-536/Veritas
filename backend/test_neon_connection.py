#!/usr/bin/env python3
"""
Test script to verify Neon DB connection.
Usage: python test_neon_connection.py

This script:
1. Validates DATABASE_URL format
2. Tests connection to Neon DB
3. Creates tables if not exist
4. Runs basic health checks
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def test_connection():
    """Test Neon DB connection."""
    print_header("NEON DB CONNECTION TEST")
    
    # Check DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("\nTo set it:")
        print("  Windows (CMD):  set DATABASE_URL=postgresql://...")
        print("  Windows (PS):   $env:DATABASE_URL='postgresql://...'")
        print("  Linux/Mac:      export DATABASE_URL='postgresql://...'")
        print("\nFor Neon DB setup, see NEON_DB_SETUP.md")
        return False
    
    print(f"✓ DATABASE_URL is set")
    
    # Validate format
    if "postgresql" not in database_url:
        print("❌ ERROR: DATABASE_URL must contain 'postgresql://'")
        return False
    
    print(f"✓ DATABASE_URL format is valid")
    
    # Test connection
    print("\n📡 Testing database connection...")
    try:
        from database import engine
        with engine.connect() as conn:
            # Simple query to verify connection
            result = conn.execute("SELECT 1")
            print("✓ Successfully connected to Neon DB")
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\nCommon issues:")
        print("  - Connection refused: Check host and port")
        print("  - Authentication failed: Check username/password")
        print("  - SSL error: Ensure sslmode=require in connection string")
        print("  - Timeout: Check firewall and internet connection")
        return False
    
    # Initialize database
    print("\n📝 Initializing database schema...")
    try:
        from database import init_db
        init_db()
        print("✓ Database schema created/updated")
    except Exception as e:
        print(f"⚠️  Warning during schema initialization: {str(e)}")
        # Don't fail here, tables might already exist
    
    # Verify tables exist
    print("\n🔍 Verifying database tables...")
    try:
        from database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Check if tables exist
            result = conn.execute(text("""
                SELECT COUNT(*) as table_count
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """))
            table_count = result.scalar()
            
            if table_count > 0:
                print(f"✓ Found {table_count} tables in database")
                
                # List tables
                result = conn.execute(text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """))
                
                print("\n  Tables:")
                for row in result:
                    print(f"    - {row[0]}")
            else:
                print("⚠️  No tables found (database is empty)")
    
    except Exception as e:
        print(f"⚠️  Could not verify tables: {str(e)}")
    
    # Connection pool info
    print("\n🔌 Connection Pool Configuration:")
    try:
        from database import engine
        pool = engine.pool
        print(f"  Pool size: {pool.size}")
        print(f"  Max overflow: {pool._max_overflow}")
        print(f"  Current connections: {pool.checkedout()}")
    except Exception as e:
        print(f"  Could not get pool info: {str(e)}")
    
    return True

def test_import():
    """Test if all modules can be imported."""
    print_header("TESTING MODULE IMPORTS")
    
    modules = [
        "database",
        "orm_models",
        "security",
        "data_access",
        "service_layer",
        "api_routes"
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"❌ {module}: {str(e)}")
            all_ok = False
    
    return all_ok

def main():
    """Main test flow."""
    print("\n")
    print("█" * 60)
    print("█  VERITAS BACKEND - NEON DB CONNECTION TEST")
    print("█" * 60)
    
    # Test imports first
    imports_ok = test_import()
    if not imports_ok:
        print("\n⚠️  Some imports failed. Install dependencies:")
        print("   pip install -r requirements_db.txt")
        return 1
    
    # Test connection
    connection_ok = test_connection()
    
    # Summary
    print_header("TEST SUMMARY")
    if connection_ok:
        print("✓ All tests passed!")
        print("\n✨ Your Neon DB is ready to use!")
        print("\nNext steps:")
        print("  1. Run the backend: uvicorn api_routes:app --reload")
        print("  2. Visit http://localhost:8000/docs for API documentation")
        print("  3. Check Neon console at https://console.neon.tech for monitoring")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nFor help:")
        print("  - See NEON_DB_SETUP.md for detailed setup instructions")
        print("  - Check DATABASE_URL format in documentation")
        print("  - Verify Neon project status at https://console.neon.tech")
        return 1

if __name__ == "__main__":
    exit_code = main()
    print("\n")
    sys.exit(exit_code)
