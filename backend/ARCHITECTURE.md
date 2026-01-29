# VERITAS Platform: Production-Grade Backend Architecture

## Overview

This document describes the complete backend architecture for the Veritas exam monitoring and proctoring platform. The system integrates real-time monitoring, integrity analysis, and dropout risk classification with a role-based access control (RBAC) system and PostgreSQL persistence layer.

**Key principles:**
- Security & data isolation (RBAC at query level)
- Scalability (denormalization for analytics, materialized views)
- Auditability (comprehensive logging)
- Non-blocking event ingestion (batch operations, connection pooling)
- Production-grade error handling and transaction safety

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React/Vue)                         │
│  - Student Dashboard | Teacher Dashboard | Admin Panel          │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  API LAYER (FastAPI Routers)                    │
│  - Authentication | Student Routes | Teacher Routes            │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              SERVICE LAYER (Business Logic)                     │
│  - data_access.py | service_layer.py                           │
│  - Monitoring ingestion | Analysis integration | RBAC checks    │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ORM LAYER (SQLAlchemy)                         │
│  - orm_models.py | Relationships | Constraints                 │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              DATABASE LAYER (PostgreSQL)                        │
│  - Connection pooling | Transactions | Materialized views      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Schema Design

### Core Tables

#### **users**
Stores authentication credentials and role assignment for all platform users.

```sql
users
├── id (UUID, PK)
├── email, username (UNIQUE)
├── password_hash (bcrypt)
├── role (ENUM: student, teacher, admin)
├── is_active, is_verified
├── last_login, last_login_ip
├── metadata (JSONB: profile_image, preferences, etc.)
└── indexes: email, role, active_role
```

**Why:** Centralized auth store. Role serves as discriminator for role-based queries.

---

#### **student_profiles** & **teacher_profiles**
Extended profiles linked to users via foreign key.

```sql
student_profiles
├── id (UUID, PK)
├── user_id (UUID, FK → users, UNIQUE)
├── enrollment_id, cohort
├── cumulative_integrity_score (0-1, denormalized)
├── cumulative_lmi (Learning Momentum Index)
├── total_exams_attempted, passed
├── current_dropout_risk (ENUM)
├── flagged_for_review
└── indexes: dropout_risk, flagged
```

**Design decision:** Denormalized scores for O(1) dashboard queries. Updated after each exam completion.

---

#### **exams**
Exam templates created by teachers.

```sql
exams
├── id (UUID, PK)
├── creator_id (FK → users)
├── title, description, subject, topic
├── max_score, duration_minutes, passing_score
├── is_published, enable_monitoring, enable_integrity_analysis
├── metadata (JSONB: custom rules, rubrics)
└── indexes: creator_published, subject_topic, published
```

---

#### **exam_attempts**
Core table: one record per student exam attempt. Stores score, integrity metrics, and submission data.

```sql
exam_attempts
├── id (UUID, PK)
├── exam_id (FK → exams)
├── student_id (FK → users)
├── status (ENUM: in_progress, completed, abandoned)
├── score, max_score, percentage, passed
├── integrity_score, lmi, dropout_label
├── flagged
├── started_at, completed_at, duration_seconds
├── submission_data (JSONB: responses, drafts)
├── metadata (JSONB: client IP, browser, proctoring info)
└── indexes: exam_student, student_status, dropout_risk, flagged, completed_at
```

**Why:** JSONB submission_data avoids schema churn. Integrity metrics stored here for fast access by students viewing their own data.

---

#### **monitoring_events**
Real-time events during exam (high-volume, append-only).

```sql
monitoring_events
├── id (UUID, PK)
├── exam_attempt_id (FK → exam_attempts)
├── student_id (FK → users)
├── event_type (e.g., eye_movement, window_focus, keystroke)
├── severity (ENUM: normal, warning, critical)
├── data_payload (JSONB: raw sensor data, coordinates, etc.)
├── is_anomaly, anomaly_score
├── description, analysis_notes
├── client_timestamp, server_timestamp
└── indexes: attempt_id, student_id, type_severity, is_anomaly, server_timestamp, payload (GIN)
```

**Design:** 
- High cardinality table (millions of records for large installations)
- GIN index on JSONB payload for efficient filtering
- Partition by date in production (`exam_attempts_2026_01`)
- Archive events older than 90 days

---

#### **behavior_analysis**
Post-attempt aggregated analysis (one record per exam_attempt).

```sql
behavior_analysis
├── id (UUID, PK)
├── exam_attempt_id (UUID, FK, UNIQUE)
├── student_id (FK → users)
├── total_monitoring_events, anomaly_count, critical_events
├── integrity_score, originality_indicators
├── lmi_score, improvement_trend
├── dropout_label, dropout_confidence
├── llm_summary, llm_recommendations, llm_model_version
├── requires_instructor_attention, requires_recap
└── indexes: attempt_id, student_id, dropout_label, flagged, completed_at
```

**Why:** UNIQUE constraint ensures one analysis per attempt. Stores LLM output for auditability.

---

#### **performance_metrics**
Denormalized aggregate stats per student (one record per student).

```sql
performance_metrics
├── id (UUID, PK)
├── student_id (UUID, FK, UNIQUE)
├── total_attempts, total_passed, avg_score
├── strengths, weaknesses (JSON arrays)
├── subject_scores (JSONB: {Math: 85, Physics: 72})
├── avg_integrity_score, integrity_trend
├── avg_lmi, lmi_trend
├── current_risk_label, flagged_for_intervention
├── last_updated, last_attempt_date
└── indexes: student_risk, flagged, student_id
```

**Updated by:** `update_performance_metrics()` after exam completion. Enables sub-millisecond dashboard loads.

---

#### **teacher_exam_permissions**
RBAC bridge: maps teachers to exams they can manage.

```sql
teacher_exam_permissions
├── teacher_id (FK → teacher_profiles)
├── exam_id (FK → exams)
├── can_view, can_edit, can_view_analytics (BOOLEAN)
├── granted_at
└── Primary key: (teacher_id, exam_id)
```

**Purpose:** Teachers can only access exams they created or are explicitly authorized for. Queries filter by this table.

---

#### **audit_logs**
Compliance trail for sensitive operations.

```sql
audit_logs
├── id (UUID, PK)
├── user_id (FK → users)
├── action (login, view_student_data, modify_exam)
├── resource_type, resource_id
├── details (JSONB)
├── ip_address, user_agent
├── created_at
└── indexes: user_action, resource, created_at
```

---

### Materialized Views

**exam_performance_summary** - Pre-computed exam stats (refreshed hourly):
```sql
SELECT exam_id, title, subject, unique_students, total_attempts, 
       avg_score, pass_rate, avg_integrity, high_risk_count, last_attempt
FROM exam_attempts
GROUP BY exam_id
```

**student_risk_summary** - Pre-computed student risk profile:
```sql
SELECT student_id, current_dropout_risk, cumulative_integrity,
       cumulative_lmi, attempt_count, flagged_count, last_attempt
```

---

## Authentication & Authorization

### Password Hashing

```python
# Use bcrypt with 12 rounds (resistant to GPU brute-force)
hash_password("secure_password")  # Returns: $2b$12$...
verify_password("input", "$2b$12$...")  # Returns: bool
```

### JWT Token Structure

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "student@example.com",
  "role": "student",
  "iat": 1674835200,
  "exp": 1674921600
}
```

**Token lifecycle:**
- Access token: 24 hours
- Refresh token: 7 days (use to obtain new access token)
- Revocation: Token blacklist in-memory (upgrade to Redis in production)

### Role-Based Access Control (RBAC)

```python
PERMISSIONS = {
    "student": {
        "view_own_profile": True,
        "view_own_exams": True,
        "view_own_integrity_score": True,
        "view_other_student_data": False,
        "create_exam": False,
    },
    "teacher": {
        "create_exam": True,
        "view_assigned_exams": True,
        "view_student_attempts": True,
        "view_behavior_analysis": True,
        "manage_students": True,
    },
    "admin": {
        "view_all_data": True,
        "manage_users": True,
    }
}
```

**Implementation:**
- Check role in each endpoint: `@require_role("teacher")`
- Filter queries by role: `can_access_student_data(role, accessor_id, target_student_id)`
- Audit all sensitive operations: `log_access(user_id, action, resource_id)`

---

## Data Access Patterns

### Student Access (Read-Only)

```python
# Student can only see their own data
def get_student_dashboard_data(student_id, db):
    attempt = db.query(ExamAttempt).filter(
        ExamAttempt.student_id == student_id
    ).first()
    
    return {
        "profile": {...},
        "exam_history": [...],
        "integrity_status": {...},
        "dropout_risk": {...}
    }
```

**What student sees:**
- Own profile, exam scores, integrity status
- Recommendations for improvement
- Monitoring events from own exams (not raw, but summary)
- Behavioral feedback

**What student does NOT see:**
- Other students' data
- Teachers' identities/contacts
- Raw monitoring event data
- LLM reasoning (only summary)

---

### Teacher Access (Filtered by Authorization)

```python
# Teacher can only see exams they created or are authorized for
def get_teacher_exam_analytics(teacher_id, exam_id, db):
    # Verify authorization
    permission = db.query(TeacherExamPermission).filter(
        and_(
            TeacherExamPermission.teacher_id == teacher_id,
            TeacherExamPermission.exam_id == exam_id,
            TeacherExamPermission.can_view_analytics == True
        )
    ).first()
    
    if not permission:
        raise PermissionError("Not authorized for this exam")
    
    # Return aggregated stats + per-student breakdowns
    return {
        "exam": {...},
        "analytics": {...},
        "students": [
            {
                "student_id": "...",
                "attempts": [...],
                "integrity_score": 0.85,
                "dropout_label": "safe"
            }
        ]
    }
```

**What teacher sees:**
- Exams they created (full access)
- Exams they're authorized for (as specified by permissions)
- All students' data for those exams
- Detailed monitoring events and behavior analysis
- Alerts and anomalies
- Actionable insights (flagged students, trends)

**Query efficiency:**
```sql
SELECT ea.* FROM exam_attempts ea
JOIN teacher_exam_permissions tep ON ea.exam_id = tep.exam_id
WHERE tep.teacher_id = ? AND tep.can_view_analytics = true
```

---

## Monitoring Data Ingestion

### Non-Blocking Event Recording

Critical for high-frequency sensor data (eye tracking, keystroke events, etc.)

```python
# Called frequently (10+ events/sec per student)
@app.post("/monitor/events")
async def record_event(request: MonitoringEventRequest, db: Session):
    event = MonitoringEvent(
        exam_attempt_id=request.attempt_id,
        event_type=request.event_type,
        severity=request.severity,
        data_payload=request.data,  # Raw JSONB
        server_timestamp=datetime.utcnow()
    )
    
    db.add(event)
    db.commit()  # Batched, uses connection pooling
    
    return {"id": str(event.id), "status": "recorded"}
```

**Optimization strategies:**

1. **Connection pooling:** SQLAlchemy QueuePool (10 connections + 20 overflow)
2. **Batch operations:** Collect events in memory, bulk insert every N seconds
3. **Partitioning:** Events by date table (`monitoring_events_2026_01`)
4. **Retention:** Archive old events (>90 days) to cold storage
5. **Indexing:** Composite index on (exam_attempt_id, server_timestamp)

### Materialized View Refresh

```python
# Nightly job (low-traffic window)
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    lambda: db.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY exam_performance_summary"),
    'cron', hour=2, minute=0
)
scheduler.start()
```

---

## Integration with Existing Modules

### Monitoring Module

Existing monitoring API (`Monitoring/app/routers/monitoring.py`) can submit raw events to Veritas backend:

```python
# From Monitoring module
response = requests.post(
    "http://veritas-backend/api/monitor/events",
    json={
        "attempt_id": "550e8400...",
        "event_type": "eye_movement",
        "severity": "warning",
        "data": {
            "x": 640, "y": 480, "confidence": 0.95,
            "gaze_point": "center"
        }
    },
    headers={"Authorization": f"Bearer {token}"}
)
```

### Scoring Module

After exam completion, scoring module calls behavior analysis:

```python
from service_layer import save_behavior_analysis

# Compute using existing modules
integrity = analyze_thinking_quality(draft1, draft2)  # From llm_engine.py
lmi = calculate_lmi([draft1, draft2])  # From scoring.py
dropout_label = detect_dropout(integrity, lmi)  # From scoring.py

# Store in database
behavior = save_behavior_analysis(
    attempt_id=attempt.id,
    student_id=attempt.student_id,
    integrity_score=integrity,
    lmi_score=lmi,
    dropout_label=dropout_label,
    llm_summary="Student shows consistent thinking patterns..."
)
```

---

## Security Considerations

### 1. SQL Injection Prevention
- Use parameterized queries (SQLAlchemy ORM)
- Input validation at API layer (Pydantic models)

### 2. Data Isolation
- Row-level security: Query filters ensure students see only own data
- Column-level security: Sensitive fields (password_hash) never exposed
- Database user with least-privilege permissions

### 3. Password Security
- Bcrypt hashing (12 rounds = ~200ms per hash)
- Never log passwords or tokens
- HTTPS-only transmission

### 4. Token Security
- JWT signed with strong secret (HMAC-SHA256)
- Short expiration (24h access, 7d refresh)
- Revocation blacklist for logout
- Rotate secret quarterly in production

### 5. Audit Trail
Every sensitive operation logged:
```python
log_audit(
    user_id="550e8400...",
    action="view_student_data",
    resource_type="student_profile",
    resource_id="550e8401...",
    ip_address="203.0.113.45",
    details={"exam_id": "550e8402..."}
)
```

---

## Performance & Scaling

### Query Performance Targets

| Operation | Target | Index Strategy |
|-----------|--------|-----------------|
| Student dashboard load | <100ms | `performance_metrics` denormalized |
| Teacher exam analytics | <500ms | `exam_performance_summary` MV |
| Monitoring event ingestion | <10ms | Bulk insert, connection pool |
| Find flagged students | <1s | `idx_behavior_flagged` |

### Connection Pooling

```python
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,           # Minimum connections
    max_overflow=20,        # Additional on-demand
    pool_pre_ping=True,     # Verify connections
)
```

### Horizontal Scaling

1. **Database read replicas:** Analytics queries → replicas
2. **Microservice separation:** Monitoring ingestion in separate service
3. **Cache layer:** Redis for session tokens, dashboard data
4. **Message queue:** Kafka for event streaming, async analysis

### Indexing Strategy

**High-cardinality indexes (frequent WHERE clauses):**
```sql
CREATE INDEX idx_exam_student ON exam_attempts(exam_id, student_id);
CREATE INDEX idx_event_attempt ON monitoring_events(exam_attempt_id);
CREATE INDEX idx_audit_user_action ON audit_logs(user_id, action);
```

**JSONB queries:**
```sql
-- Find events with specific payload values
SELECT * FROM monitoring_events 
WHERE data_payload @> '{"gaze_area": "keyboard"}';

-- Use GIN index for performance
CREATE INDEX idx_event_payload ON monitoring_events USING GIN (data_payload);
```

---

## Deployment Checklist

### Prerequisites
- PostgreSQL 13+
- Python 3.9+
- Redis (for token blacklist, session management)

### Environment Setup

```bash
# .env
DATABASE_URL=postgresql://user:password@host:5432/veritas_db
JWT_SECRET=your-256-bit-secret-key
BCRYPT_ROUNDS=12
DEBUG=False
LOG_LEVEL=INFO
```

### Database Initialization

```python
from database import init_db
from orm_models import Base

# Run once on deployment
init_db()
```

### Monitoring & Alerting

```python
# Monitor key metrics
- Event ingestion latency (target: <10ms)
- Query latency (p95: <500ms for analytics)
- Database connection pool utilization
- Audit log volume (alert if > 10k/min)
- Failed authentication attempts (alert if > 5/min from same IP)
```

---

## API Endpoints Summary

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Generate JWT token
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Revoke token

### Student Endpoints
- `GET /student/dashboard` - Student dashboard data
- `GET /student/exams/available` - List available exams
- `POST /student/exams/{exam_id}/start` - Start exam attempt
- `POST /student/exams/{attempt_id}/submit` - Submit exam
- `GET /student/attempts/{attempt_id}` - View past attempt detail

### Teacher Endpoints
- `GET /teacher/dashboard` - Teacher dashboard
- `POST /teacher/exams` - Create exam
- `GET /teacher/exams/{exam_id}/analytics` - Exam analytics
- `GET /teacher/students/{student_id}` - Student detail
- `GET /teacher/attempts/{attempt_id}/monitoring` - Monitoring events
- `GET /teacher/alerts` - High-priority alerts

### Admin Endpoints
- `GET /admin/users` - List users
- `POST /admin/users/{user_id}/lock` - Lock user account
- `GET /admin/audit-logs` - View audit trail

---

## Maintenance

### Regular Tasks

**Daily:**
- Monitor connection pool utilization
- Check audit log volume
- Review failed auth attempts

**Weekly:**
- Refresh materialized views
- Analyze query performance logs
- Archive monitoring events older than 90 days

**Monthly:**
- Vacuum analyze full database
- Review and rotate secrets
- Capacity planning

---

## Support & Troubleshooting

### Common Issues

**Q: Slow dashboard queries**
- A: Check `performance_metrics` is populated. Run ANALYZE. Check index usage.

**Q: Monitoring events not persisting**
- A: Check database connection pool. Monitor error logs. Verify foreign keys.

**Q: Teacher can't see student data**
- A: Verify `teacher_exam_permissions` grant. Check `can_view_analytics` flag.

**Q: Token validation errors**
- A: Verify JWT_SECRET matches. Check token expiration. Check revocation blacklist.

---

## References

- SQLAlchemy ORM: https://docs.sqlalchemy.org/
- PostgreSQL JSONB: https://www.postgresql.org/docs/current/datatype-json.html
- JWT Best Practices: https://tools.ietf.org/html/rfc8725
- OWASP Database Security: https://owasp.org/www-community/attacks/SQL_Injection
