# PostgreSQL via NeonDB Integration Guide

## Overview
All backend services in the Veritas project are now configured to use PostgreSQL database hosted on NeonDB (serverless PostgreSQL). This replaces the previous in-memory storage with persistent, cloud-based database storage.

## Affected Backends
- **Monitoring2.0/backend** - Monitoring logs and system health
- **staffstuddash/backend** - Student performance and assessments
- **dropout** - Dropout detection events and predictions

## Quick Setup (5 minutes)

### 1. Create NeonDB Account
```bash
# Visit https://neon.tech
# Sign up (free tier available)
# Create a new project
# Copy the connection string
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and update:

```bash
# In /Veritas/.env
DATABASE_URL=postgresql://user:password@ep-xxxx.us-east-1.neon.tech/neondb?sslmode=require
```

### 3. Install Dependencies
Each backend needs SQLAlchemy and psycopg2:

```bash
# Monitoring2.0
cd Monitoring2.0/backend
pip install -r requirements.txt

# staffstuddash
cd staffstuddash/backend
pip install -r requirements.txt

# dropout
cd dropout
pip install sqlalchemy psycopg2-binary python-dotenv
```

### 4. Run Your Backend
```bash
# All backends will automatically:
# - Connect to PostgreSQL
# - Create tables on first run
# - Use in-memory fallback if database unavailable
python main.py
```

## Architecture

### Database Setup
```
Your Machine (FastAPI App)
    ↓
Environment Variable: DATABASE_URL
    ↓
SQLAlchemy Engine (NullPool for Neon)
    ↓
NeonDB PostgreSQL (Cloud)
    ↓
Persistent Data Storage
```

### Key Components

#### 1. Shared Utils (`shared_db_utils.py`)
```python
from shared_db_utils import db_manager, get_db

# Use in your code:
with db_manager.session_scope() as session:
    # perform queries
```

#### 2. Database Models

**Monitoring2.0**: `app/models/monitoring_models.py`
- MonitoringLog - Individual log entries
- MonitoringResult - Analysis results
- SystemHealth - Overall health status

**staffstuddash**: `backend/db_models.py`
- Student - Student profiles
- Draft - Student submissions
- AssessmentLog - Test results
- PerformanceRecord - Analytics

**dropout**: `db_models.py`
- Student - Student records
- LearningEvent - Activity tracking
- Assessment - Test scores
- DropoutPrediction - Predictions

#### 3. Database Manager Classes

Each backend has a manager class:
```python
# Monitoring2.0
from app.utils.database import monitoring_db
monitoring_db.add_log(log_data)

# staffstuddash
from datastore import datastore
datastore.add_student(student_id, name, email)

# dropout
from database import db_manager
db_manager.add_learning_event(event_id, student_id, ...)
```

## Usage Examples

### Monitoring2.0
```python
from app.utils.database import monitoring_db

# Add a log
log = MonitoringLogSchema(...)
event_id = monitoring_db.add_log(log)

# Query logs
logs, total = monitoring_db.get_logs(
    source="api_server",
    status=HealthStatus.WARNING,
    limit=100
)

# Get statistics
stats = monitoring_db.get_statistics()
```

### staffstuddash
```python
from datastore import datastore

# Add student
student = datastore.add_student("s001", "John Doe", "john@example.com")

# Add assessment
assessment = datastore.add_assessment(
    "s001", 
    type="exam",
    subject="Math",
    score=85.0
)

# Update performance
datastore.update_performance_record("s001", {
    "integrity_score": 0.85,
    "grit_level": 0.7,
    "status": "Active"
})
```

### dropout
```python
from database import db_manager

# Add student
student = db_manager.add_student("s001", "Jane Smith", "jane@example.com")

# Add learning event
event = db_manager.add_learning_event(
    "evt001",
    student_id="s001",
    question_id="q123",
    event_type="QUESTION_SUBMIT"
)

# Save prediction
prediction = db_manager.save_prediction(
    "pred001",
    student_id="s001",
    dropout_type="COGNITIVE",
    risk_score=0.75,
    risk_level="HIGH"
)
```

## Fallback Mechanism

If PostgreSQL is unavailable, the system automatically falls back to in-memory storage:

```python
if datastore.use_fallback:
    print("Using in-memory storage - database unavailable")
```

This ensures:
- Development works without database setup
- Graceful degradation in production
- No breaking changes to existing code

## Database Connection String Format

### NeonDB (Production)
```
postgresql://user:password@ep-xxxx.us-east-1.neon.tech/neondb?sslmode=require
```

### Local PostgreSQL (Development)
```
postgresql://postgres:password@localhost:5432/veritas_db
```

### Optional Parameters
- `?sslmode=require` - Force SSL (recommended for NeonDB)
- `?connect_timeout=10` - Connection timeout
- `?statement_timeout=30000` - Query timeout (30s)

## Environment Variables

### Required
- `DATABASE_URL` - PostgreSQL connection string

### Optional
- `DEBUG` - Set to "true" for SQL logging
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)

### Monitoring2.0 Specific
- `ENABLE_LLM_MONITORING` - Enable LLM analysis
- `GROQ_API_KEY` - Groq API key
- `WARNING_THRESHOLD` - Alert threshold

## Migration from In-Memory Storage

The system handles migration automatically:

1. **First Run**: Tables are created automatically
2. **Schema**: Existing Pydantic models are mapped to SQLAlchemy models
3. **Data**: Previous in-memory data is lost (fresh start with DB)

To migrate existing data:
```python
# Export from in-memory
old_data = json.load(open("backup.json"))

# Import to database
for item in old_data:
    datastore.add_student(item["id"], item["name"], item["email"])
```

## Troubleshooting

### Connection Refused
```
Error: could not connect to server: Connection refused
```
**Solution**: Check DATABASE_URL and ensure PostgreSQL is running

### SSL Error
```
SSL: CERTIFICATE_VERIFY_FAILED
```
**Solution**: Add `?sslmode=require` to NeonDB URLs

### Table Already Exists
```
Error: relation "students" already exists
```
**Solution**: Database already initialized, this is normal on subsequent runs

### Timeout Error
```
OperationalError: server closed the connection unexpectedly
```
**Solution**: NeonDB has idle connection timeout. Add to DATABASE_URL:
```
?connect_timeout=10
```

## Performance Tips

1. **Connection Pooling**: NullPool is used for NeonDB (serverless-friendly)
2. **Batch Operations**: Use sessions for multiple operations
3. **Indexing**: Add indexes on frequently queried columns
4. **Query Optimization**: Use filters in database queries, not Python

```python
# Good: Filter in database
logs, count = monitoring_db.get_logs(source="api")

# Avoid: Filter in Python
logs = monitoring_db.get_logs()
logs = [l for l in logs if l.source == "api"]
```

## Security

1. **Environment Variables**: Never commit `.env` with real credentials
2. **SSL Connections**: Always use `?sslmode=require` for NeonDB
3. **Connection Strings**: Treat as secrets, rotate periodically
4. **SQL Injection**: SQLAlchemy ORM prevents SQL injection automatically

## Next Steps

1. Create NeonDB account
2. Update `.env` with your connection string
3. Install dependencies: `pip install -r requirements.txt`
4. Run backend: `python main.py`
5. Verify connection in logs

## Support

- NeonDB Docs: https://neon.tech/docs
- SQLAlchemy: https://docs.sqlalchemy.org
- psycopg2: https://www.psycopg.org/
