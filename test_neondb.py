#!/usr/bin/env python3
"""
Simple NeonDB Connection Test
Tests if your connection string works
"""

import os
import sys

# Read .env file
print("=" * 60)
print("NeonDB Connection Test")
print("=" * 60)

# Try to read DATABASE_URL from .env
try:
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("DATABASE_URL="):
                db_url = line.split("=", 1)[1].strip()
                # Mask password for display
                masked = db_url.split("@")[0] + "@***@" + db_url.split("@")[1] if "@" in db_url else db_url
                print(f"\n✓ DATABASE_URL found in .env")
                print(f"  Connection: {masked}")
                
                # Try SQLAlchemy connection
                try:
                    from sqlalchemy import create_engine, text
                    from sqlalchemy.pool import NullPool
                    
                    print(f"\n⏳ Testing PostgreSQL connection...")
                    engine = create_engine(db_url, poolclass=NullPool, echo=False)
                    
                    with engine.connect() as conn:
                        result = conn.execute(text("SELECT 1 as test"))
                        result.close()
                    
                    print(f"✓ PostgreSQL connection SUCCESSFUL!")
                    print(f"\n" + "=" * 60)
                    print(f"✓ Your NeonDB is connected and working!")
                    print(f"=" * 60)
                    print(f"\nNext steps:")
                    print(f"1. Install requirements: pip install -r requirements.txt")
                    print(f"2. Start backend: cd Monitoring2.0/backend && python main.py")
                    print(f"3. Test API: http://localhost:8000")
                    
                except ImportError:
                    print(f"⚠ SQLAlchemy not installed")
                    print(f"  Run: pip install sqlalchemy psycopg2-binary")
                    
                except Exception as e:
                    print(f"✗ Connection failed: {str(e)}")
                    print(f"\nTroubleshooting:")
                    print(f"1. Check DATABASE_URL is correct in .env")
                    print(f"2. Verify NeonDB project is running")
                    print(f"3. Check internet connection")
                    
                break
        else:
            print(f"\n✗ DATABASE_URL not found in .env")
            print(f"\nTo fix:")
            print(f"1. Open .env file")
            print(f"2. Add: DATABASE_URL=postgresql://...")
            
except FileNotFoundError:
    print(f"\n✗ .env file not found")
    print(f"\nTo fix:")
    print(f"1. Create .env file in Veritas/ directory")
    print(f"2. Add your NeonDB connection string")
    print(f"3. Run this script again")

print(f"\n" + "=" * 60)
