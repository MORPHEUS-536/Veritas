# Architecture & Design Decisions

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Veritas Backend                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────┐  ┌────────────────────────────────┐ │
│  │ Monitoring2.0      │  │ staffstuddash                  │ │
│  │ Backend (FastAPI)  │  │ Backend (FastAPI)              │ │
│  │                    │  │                                │ │
│  │ - MonitoringLog    │  │ - Student Management           │ │
│  │ - HealthStatus     │  │ - Assessment Tracking          │ │
│  │ - Analytics        │  │ - Performance Records          │ │
│  └────────────────────┘  └────────────────────────────────┘ │
│           │                           │                      │
│  ┌────────────────────┐               │                      │
│  │ dropout            │               │                      │
│  │ Detection System   │               │                      │
│  │                    │               │                      │
│  │ - LearningEvent    │               │                      │
│  │ - Prediction       │               │                      │
│  │ - Analytics        │               │                      │
│  └────────────────────┘               │                      │
│           │                           │                      │
└───────────┼───────────────────────────┼──────────────────────┘
            │                           │
            └───────────────┬───────────┘
                            │
                    ┌───────▼────────┐
                    │  Environment   │
                    │  DATABASE_URL  │
                    └────────────────┘
                            │
                    ┌───────▼─────────────┐
                    │   SQLAlchemy ORM    │
                    │ - Session Factory   │
                    │ - Engine (NullPool) │
                    └─────────┬───────────┘
                              │
                    ┌─────────▼──────────┐
                    │  PostgreSQL Driver │
                    │   (psycopg2)       │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │   PostgreSQL       │
                    │                    │
                    │   NeonDB Cloud     │
                    │   (or Local)       │
                    └────────────────────┘
```

## Data Flow

### Write Operation
```
Application Code
    ↓
Database Manager (datastore / monitoring_db / db_manager)
    ↓
SQLAlchemy ORM (Maps Python objects to SQL)
    ↓
psycopg2 Driver (PostgreSQL communication)
    ↓
NeonDB PostgreSQL (Persistent storage)
```

### Read Operation
```
Application Code (Query request)
    ↓
Database Manager (Build query with filters)
    ↓
SQLAlchemy ORM (Translate to SQL with WHERE clauses)
    ↓
PostgreSQL (Execute indexed query)
    ↓
psycopg2 (Return results)
    ↓
SQLAlchemy (Convert rows to objects)
    ↓
Application Code (Receives data)
```

## Design Decisions

### 1. Why NullPool for Neon?
**Decision**: Use `NullPool` instead of `QueuePool`

**Rationale**:
- Neon is serverless - connections are expensive
- NullPool creates fresh connection per request
- Avoids idle connection timeout issues
- Recommended by Neon documentation

```python
create_engine(url, poolclass=NullPool)
```

### 2. Why SQLAlchemy ORM?
**Decision**: Use ORM instead of raw SQL

**Rationale**:
- Type safety and autocomplete
- SQL injection prevention
- Database agnostic (can switch backends)
- Easier to maintain and understand
- Less boilerplate code

```python
# ORM (Type-safe, readable)
session.query(Student).filter(Student.id == "s001").first()

# vs Raw SQL (Error-prone)
cursor.execute("SELECT * FROM students WHERE id = %s", ("s001",))
```

### 3. Why Keep Backward Compatibility?
**Decision**: Maintain same API for database operations

**Rationale**:
- Minimal code changes needed
- Easy migration path
- Can test without changing application
- Same function signatures work
- Reduces risk of bugs

```python
# Same interface, different backend
datastore.add_student(...)  # Works with both old/new
monitoring_db.get_logs(...) # Same function signature
```

### 4. Why Fallback to In-Memory?
**Decision**: Automatic fallback if PostgreSQL unavailable

**Rationale**:
- Development without database setup
- Graceful degradation in production
- No breaking changes
- Can start with fallback, add DB later

```python
if datastore.use_fallback:
    # Using in-memory storage
```

### 5. Why Environment Variables?
**Decision**: Store credentials in environment, not code

**Rationale**:
- Never commit secrets to git
- Different configs per environment
- Easy deployment configuration
- Industry standard practice
- Follows 12-factor app principles

```bash
# .env (not committed)
DATABASE_URL=postgresql://...

# Code (no secrets)
db_url = os.getenv("DATABASE_URL")
```

## Connection Pooling Strategy

```
Request 1 → Fresh Connection → Query → Close Connection
Request 2 → Fresh Connection → Query → Close Connection
Request 3 → Fresh Connection → Query → Close Connection

Benefits:
✓ No idle connections
✓ No timeout issues
✓ Fresh connection state
✓ Serverless-friendly
✓ Cost-effective with Neon
```

## Transaction Management

```python
# Context manager pattern
session = db_manager.get_session()
try:
    session.add(obj)
    session.commit()  # Auto-rollback on error
except Exception:
    session.rollback()
finally:
    session.close()
```

## Scalability Considerations

### Current (Single Backend Instance)
```
API Request → Database Session → PostgreSQL → Response
```

### Future (Multiple Backend Instances)
```
API Request 1 ┐
API Request 2 ├→ Load Balancer → Database Sessions → PostgreSQL (Shared)
API Request 3 ┘
```

PostgreSQL handles:
- Connection pooling
- Concurrent requests
- Transaction isolation
- ACID guarantees

## Security Model

```
┌─────────────────┐
│  Application    │  Never stores credentials
├─────────────────┤
│   .env file     │  Sensitive data (not in git)
├─────────────────┤
│  Environment    │  Runtime configuration
├─────────────────┤
│  SQLAlchemy     │  Parameterized queries (SQL injection safe)
├─────────────────┤
│  psycopg2       │  Encrypted connection (SSL with Neon)
├─────────────────┤
│  NeonDB         │  Enterprise-grade security
└─────────────────┘
```

## Model Organization

### Monitoring2.0
```
Models (app/models/monitoring_models.py)
├── MonitoringLog
├── MonitoringResult
└── SystemHealth

Database (app/utils/database.py)
├── MonitoringDatabase class
├── initialize_database()
└── monitoring_db instance
```

### staffstuddash
```
Models (db_models.py)
├── Student
├── Draft
├── AssessmentLog
├── PerformanceRecord
└── ActionLog

Database (datastore.py)
├── DatastoreManager class
├── datastore instance
└── Legacy functions
```

### dropout
```
Models (db_models.py)
├── Student
├── LearningEvent
├── Assessment
├── FeatureSet
└── DropoutPrediction

Database (database.py)
├── DropoutDatabaseManager class
├── db_manager instance
└── get_db() dependency
```

## Testing Strategy

### Unit Tests
```python
# Test database operations
def test_add_student():
    student = datastore.add_student("s001", "Name", "email")
    assert student.id == "s001"

# Test queries
def test_get_student():
    student = datastore.get_student("s001")
    assert student.name == "Name"
```

### Integration Tests
```python
# Test full pipeline
def test_assessment_workflow():
    student = datastore.add_student("s001", "Name", "email")
    assessment = datastore.add_assessment("s001", "exam", "Math", 85)
    record = datastore.get_performance_record("s001")
    assert record is not None
```

### Connection Tests
```bash
python verify_database.py
# ✓ PostgreSQL connection successful
# ✓ All tables created/verified
```

## Performance Optimization

### Indexing Strategy
```sql
-- Created automatically for primary keys
CREATE INDEX idx_logs_source ON monitoring_logs(source);
CREATE INDEX idx_logs_timestamp ON monitoring_logs(timestamp);
CREATE INDEX idx_assessments_student ON assessment_logs(student_id);
```

### Query Optimization
```python
# Good: Filter in database
logs, count = monitoring_db.get_logs(source="api", limit=100)

# Bad: Filter in Python (loads all data)
logs = monitoring_db.get_logs(limit=999999)
logs = [l for l in logs if l.source == "api"]
```

### Batch Operations
```python
# Good: Single session for batch
session = db.get_session()
for item in items:
    session.add(item)
session.commit()

# Bad: Multiple sessions
for item in items:
    db.add(item)  # New session each time
```

## Deployment Considerations

### Development
- Use local PostgreSQL or Neon free tier
- DATABASE_URL in .env
- Debug=True for SQL logging

### Staging
- Neon free tier or dedicated instance
- DATABASE_URL from environment
- Debug=False

### Production
- Neon paid tier or managed PostgreSQL
- DATABASE_URL from secrets manager
- Connection pooling enabled
- SSL required (sslmode=require)
- Automated backups configured
- Monitoring and alerts setup

## Disaster Recovery

### Backup Strategy
```
NeonDB automatically provides:
✓ Automated backups
✓ Point-in-time recovery
✓ Replication
✓ Data redundancy
```

### Manual Backup
```bash
# Dump database
pg_dump postgresql://user:pass@host/db > backup.sql

# Restore
psql postgresql://user:pass@host/db < backup.sql
```

## Monitoring & Observability

### Database Monitoring
```python
stats = monitoring_db.get_statistics()
# {
#     "total_logs": 1000,
#     "status_distribution": {...},
#     "oldest_log": "2024-01-28T...",
#     "newest_log": "2024-01-31T..."
# }
```

### Health Checks
```python
status, severity = monitoring_db.get_current_health_status()
# (HealthStatus.NORMAL, 0.2)
```

### Query Logging
```python
# Set DEBUG=true in .env to see SQL
DEBUG=True
# Logs all executed SQL statements
```

## Future Enhancements

### Planned
- [ ] Database migration management (Alembic)
- [ ] Caching layer (Redis)
- [ ] Query result pagination
- [ ] Advanced filtering operators
- [ ] Batch insert optimization

### Optional
- [ ] GraphQL API for database
- [ ] Full-text search
- [ ] Geospatial queries
- [ ] Time-series data analysis
- [ ] Data archival

## Migration Path

### Phase 1 (Current)
- All backends use SQLAlchemy with NeonDB
- Fallback to in-memory if needed
- Zero breaking changes

### Phase 2 (Optional)
- Add caching layer
- Implement query optimization
- Advanced monitoring

### Phase 3 (Optional)
- Microservices with shared database
- Read replicas
- Sharding strategy

---

## Summary

✅ **Transparent**: Database abstraction layer hides implementation
✅ **Scalable**: PostgreSQL supports unlimited growth
✅ **Secure**: SQL injection prevention, SSL encryption
✅ **Resilient**: Fallback mechanism, NeonDB reliability
✅ **Maintainable**: Clear separation of concerns
✅ **Testable**: Easy to mock and test
✅ **Compatible**: No breaking changes to existing code

All design decisions prioritize **simplicity, reliability, and maintainability** while enabling **enterprise-grade scalability**.
