# Neon DB Integration Guide

## Quick Setup (3 minutes)

### 1. Create Neon Project
```bash
# Visit https://console.neon.tech
# Sign up or login
# Click "Create a project"
# Choose: PostgreSQL 16
# Region: Select closest to your location
# Click "Create project"
```

### 2. Get Connection String
```bash
# In Neon console:
# Project Dashboard → Connection String → Copy "Connection string"
# Format: postgresql://user:password@host/database?sslmode=require

# Example:
# postgresql://neondb_owner:abc123@ep-quiet-wave-12345.us-east-1.aws.neon.tech/veritas_db?sslmode=require
```

### 3. Set Environment Variable
```bash
# Windows PowerShell
$env:DATABASE_URL = "postgresql://user:pass@host/database?sslmode=require"

# Windows CMD
set DATABASE_URL=postgresql://user:pass@host/database?sslmode=require

# Linux/Mac
export DATABASE_URL="postgresql://user:pass@host/database?sslmode=require"

# Or save to .env file
echo "DATABASE_URL=postgresql://user:pass@host/database?sslmode=require" > .env
```

### 4. Initialize Database
```bash
cd Veritas/backend
python -c "from database import init_db; init_db(); print('✓ Neon DB initialized')"
```

### 5. Run Backend
```bash
uvicorn api_routes:app --reload
```

**✅ Done! Backend now uses Neon DB as primary database.**

---

## Detailed Setup

### Step 1: Create Neon Account

1. Go to **https://console.neon.tech**
2. Click **"Sign Up"** (or login if you have account)
3. Create account with email/GitHub/Google
4. Verify email

### Step 2: Create Project

1. Click **"Create a project"** button
2. Configure:
   - **Name:** `veritas` (or your choice)
   - **Database name:** `veritas_db`
   - **PostgreSQL version:** 16 (latest)
   - **Region:** Select closest to you
     - US East: `us-east-1`
     - US West: `us-west-2`
     - Europe: `eu-west-1`

3. Click **"Create project"** (takes ~30 seconds)

### Step 3: Get Connection String

**From Neon Console:**

1. Navigate to **Connection String** tab (top of page)
2. Select role: `neondb_owner` (default, full permissions)
3. Copy the connection string

**You'll see:**
```
postgresql://neondb_owner:YOUR_PASSWORD@ep-quiet-wave-12345.us-east-1.aws.neon.tech/veritas_db?sslmode=require
```

**Components:**
- `neondb_owner` - Database user
- `YOUR_PASSWORD` - Auto-generated password
- `ep-quiet-wave-12345` - Neon endpoint
- `us-east-1.aws.neon.tech` - Region
- `veritas_db` - Database name
- `?sslmode=require` - SSL required (important!)

### Step 4: Set Up Environment

**Option A: .env file (recommended)**
```bash
# In Veritas/backend/ directory
cat > .env << EOF
DATABASE_URL=postgresql://neondb_owner:YOUR_PASSWORD@ep-quiet-wave-12345.us-east-1.aws.neon.tech/veritas_db?sslmode=require
JWT_SECRET=your-secret-key-min-32-chars-change-in-production
BCRYPT_ROUNDS=12
DEBUG=True
EOF
```

**Option B: Environment variable (Windows PowerShell)**
```powershell
$env:DATABASE_URL = "postgresql://neondb_owner:YOUR_PASSWORD@ep-quiet-wave-12345.us-east-1.aws.neon.tech/veritas_db?sslmode=require"
$env:JWT_SECRET = "your-secret-key-min-32-chars"
```

**Option C: Environment variable (Linux/Mac)**
```bash
export DATABASE_URL="postgresql://neondb_owner:YOUR_PASSWORD@ep-quiet-wave-12345.us-east-1.aws.neon.tech/veritas_db?sslmode=require"
export JWT_SECRET="your-secret-key-min-32-chars"
```

### Step 5: Install Dependencies

```bash
cd Veritas/backend
pip install -r requirements_db.txt
```

### Step 6: Initialize Database Schema

```bash
# This creates all tables in your Neon DB
python -c "from database import init_db; init_db(); print('✓ Database initialized with schema')"
```

**Expected output:**
```
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"
CREATE TABLE users...
CREATE TABLE exam_attempts...
...
✓ Database initialized with schema
```

### Step 7: Verify Connection

```bash
# Test connection
python -c "from database import SessionLocal, engine; \
session = SessionLocal(); \
result = session.execute('SELECT 1'); \
print('✓ Connected to Neon DB'); \
session.close()"
```

**Expected output:**
```
✓ Connected to Neon DB
```

### Step 8: Start Backend

```bash
uvicorn api_routes:app --reload
```

**Expected output:**
```
Uvicorn running on http://127.0.0.1:8000
Press CTRL+C to quit
```

### Step 9: Test API

Open browser: **http://localhost:8000/docs**

Try endpoint:
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-30T...",
  "database": "connected"
}
```

---

## Neon DB Features

### ✅ Always On
- Your database is always running
- No cold starts or restarts needed
- Serverless architecture

### ✅ Automatic Backups
- 7-day backup retention (free tier)
- Point-in-time recovery available
- Automated backup schedule

### ✅ Connection Pooling
- Built-in pgBouncer
- Handles connection management
- Optimal for serverless apps

### ✅ Branching
- Create database branches for testing
- Test schema changes safely
- Merge branches back to main

### ✅ Monitoring
- Query analytics
- Connection monitoring
- Performance insights

---

## Connection Pooling Configuration

### For Neon (Recommended)

```python
# database.py (already configured for Neon)
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,              # Neon: 5-10 is optimal
    max_overflow=10,          # Allow 10 additional connections
    pool_pre_ping=True,       # Important for serverless
    ssl_require=True
)
```

**Explanation:**
- `pool_size=5`: Maintains 5 persistent connections
- `max_overflow=10`: Can create up to 10 more as needed
- `pool_pre_ping=True`: Verifies connections before use (prevents stale connections)
- `ssl_require=True`: Enforces SSL (required by Neon)

### For High-Load Production

```python
# If you need higher throughput:
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,             # More persistent connections
    max_overflow=30,          # More overflow capacity
    pool_pre_ping=True,
    ssl_require=True
)
```

---

## Troubleshooting

### Issue: "Connection refused"
```python
# Check your CONNECTION_STRING is correct
# Verify it includes: ?sslmode=require
# Verify password doesn't have special chars (or URL-encoded)
# Test manually:
psql postgresql://neondb_owner:password@host/database?sslmode=require
```

### Issue: "FATAL: password authentication failed"
```
✓ Copy password exactly from Neon console
✓ Check for spaces or special characters
✓ Regenerate password if needed:
  - Neon Console → Security → Reset password
```

### Issue: "SSL error: certificate verify failed"
```
# This shouldn't happen with sslmode=require
# If it does:
# 1. Update SSL certificates: pip install --upgrade certifi
# 2. Check Python version: python --version (use 3.9+)
# 3. Try: export SSL_NO_VERIFY=false (testing only, not recommended)
```

### Issue: "Statement timeout"
```python
# If queries take >30 seconds:
# 1. Check query performance in Neon console
# 2. Increase timeout in database.py:
    connect_args={
        "options": "-c statement_timeout=60000"  # 60 seconds
    }
# 3. Optimize slow queries (add indexes)
```

### Issue: "Too many connections"
```python
# Reduce pool_size in database.py:
    pool_size=3,      # Reduce from 5
    max_overflow=5    # Reduce from 10
```

---

## Neon Console Features

### Monitoring
1. Go to **Monitoring** tab
2. View:
   - Active connections
   - Query performance
   - Database size
   - CPU/Memory usage

### Branching
1. Go to **Branches** tab
2. Click **"Create branch"**
3. Use for testing without affecting production

### SQL Editor
1. Click **"SQL Editor"** in left menu
2. Run SQL queries directly
3. Useful for:
   - Testing queries
   - Checking data
   - Running migrations

### Settings
1. Go to **Settings** → **Database settings**
2. Configure:
   - Connection pooling settings
   - Compute size (scale up if needed)
   - Autoscaling parameters

---

## Security Best Practices

### 1. Protect Your Password
```bash
# ❌ Don't commit to git
git update-index --skip-worktree .env

# ✅ Use environment variables
export DATABASE_URL="..."

# ✅ Use secrets manager (production)
# AWS Secrets Manager
# Google Cloud Secret Manager
# HashiCorp Vault
```

### 2. Restrict IP Access
```
In Neon Console:
→ Security → IP Whitelist
→ Add your IP addresses only
→ Production: add deployment server IPs
```

### 3. Regenerate Password Regularly
```
In Neon Console:
→ Security → Reset password
→ Do this quarterly for production
```

### 4. Use Read-Only Roles
```sql
-- Create read-only user for analytics:
CREATE USER analytics_user WITH PASSWORD 'secure_password';
GRANT USAGE ON SCHEMA public TO analytics_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_user;
```

---

## Production Deployment

### Before Going Live

1. **Upgrade Neon Plan**
   - Free tier: Good for dev/testing
   - Pro tier: Recommended for production
   - Business tier: For critical systems

2. **Configure Backups**
   - Neon automatically backs up daily
   - For critical data: Enable point-in-time recovery

3. **Set Up Monitoring**
   - Use Neon console monitoring
   - Set up Datadog/New Relic integration
   - Enable query logging

4. **Scale Compute**
   - Start with default compute
   - Upgrade if needed (Neon → Settings → Compute size)

### Deployment Configuration

```bash
# Production .env
DATABASE_URL=postgresql://neondb_owner:SECURE_PASSWORD@ep-xxxx.aws.neon.tech/veritas_db?sslmode=require
JWT_SECRET=long-random-secret-256-bits-minimum
BCRYPT_ROUNDS=12
DEBUG=False
LOG_LEVEL=WARNING
ENVIRONMENT=production
CORS_ORIGINS=["https://veritas.example.com"]
```

### Docker Deployment with Neon

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements_db.txt .
RUN pip install --no-cache-dir -r requirements_db.txt

COPY . .

CMD ["uvicorn", "api_routes:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t veritas:backend .
docker run -e DATABASE_URL="postgresql://..." -p 8000:8000 veritas:backend
```

---

## Pricing

### Neon Free Tier
- 1 project
- 3GB storage
- 100 hours compute
- Perfect for: Development, testing, small apps

### Neon Pro (Recommended)
- $$9/month
- Unlimited projects
- 500GB storage included
- Unlimited compute hours
- Priority support
- Perfect for: Production applications

### Neon Business
- Custom pricing
- Dedicated support
- Advanced security
- Perfect for: Enterprise apps

**Estimate for Veritas:**
- 100K students: ~10GB storage = Free tier sufficient (but upgrade for prod)
- 1M exam attempts: ~50GB storage = Pro tier recommended
- 10M monitoring events: ~200GB storage = Pro tier recommended

---

## Monitoring Performance

### Check Database Status
```bash
# In Neon Console:
# Dashboard → Monitoring → View live metrics
# - Active connections
# - Query performance
# - Data size
# - CPU utilization
```

### Query Analytics
```bash
# In Neon Console:
# SQL Editor → View recent queries
# Check slow queries
# Check query frequency
```

### Connect Monitoring Tools
```bash
# Datadog Integration:
# Neon Console → Integrations → Add Datadog
# Set API key
# Monitor in Datadog dashboard

# New Relic Integration:
# Similar process through Neon Integrations
```

---

## Backup & Recovery

### Automatic Backups
```
Neon automatically backs up:
- Daily snapshots (free tier: 7 days retention)
- Pro tier: 14 days retention
- Business: custom retention
```

### Manual Export
```bash
# Export entire database:
pg_dump postgresql://neondb_owner:password@host/database > backup.sql

# Export specific table:
pg_dump -t users postgresql://neondb_owner:password@host/database > users_backup.sql
```

### Restore from Backup
```bash
# Restore entire database:
psql postgresql://neondb_owner:password@host/database < backup.sql

# This recreates all tables and data
```

---

## Next Steps

1. ✅ Create Neon account (https://console.neon.tech)
2. ✅ Create project
3. ✅ Copy connection string
4. ✅ Set DATABASE_URL environment variable
5. ✅ Run: `python -c "from database import init_db; init_db()"`
6. ✅ Start backend: `uvicorn api_routes:app --reload`
7. ✅ Test API: http://localhost:8000/docs
8. ✅ Connect frontend to backend
9. ✅ Monitor in Neon console

---

## Support

- **Neon Docs:** https://neon.tech/docs
- **Neon Status:** https://status.neon.tech
- **Community:** Discord, GitHub Issues
- **Email:** support@neon.tech

---

**Status:** ✅ Veritas backend is now configured for Neon DB
**Next:** Follow quick setup above to get running in minutes
