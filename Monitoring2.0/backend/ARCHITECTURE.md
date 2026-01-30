# Monitoring System - Architecture & Design Document

## Overview

The Monitoring System is a FastAPI-based backend that continuously observes incoming data/events, detects failures and anomalies, classifies system health, and determines appropriate responses.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   API Layer  │  │ Health Check │  │ Root Routes  │      │
│  │  /events     │  │   /health    │  │    /docs     │      │
│  │  /logs       │  │   /stats     │  │   /redoc     │      │
│  │  /analysis   │  │              │  │              │      │
│  └──────┬───────┘  └──────────────┘  └──────────────┘      │
│         │                                                     │
│         ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Monitoring Engine (Core Logic)           │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  • Rule-Based Detection                             │   │
│  │    - Threshold violations                           │   │
│  │    - Invalid output detection                       │   │
│  │    - Consistency checks                             │   │
│  │    - Silent failure detection                       │   │
│  │    - Anomaly detection (z-score analysis)           │   │
│  │                                                     │   │
│  │  • Health Status Classification                     │   │
│  │    - NORMAL (0.0-0.7)                              │   │
│  │    - WARNING (0.7-0.9)                             │   │
│  │    - CRITICAL (0.9-1.0)                            │   │
│  │                                                     │   │
│  │  • Historical Data Management                       │   │
│  │    - Event history per source                       │   │
│  │    - Trend analysis                                 │   │
│  └──────┬──────────────────────────────────────────────┘   │
│         │                                                     │
│         ├─────────────────────────┬────────────────┐        │
│         ▼                         ▼                ▼        │
│  ┌─────────────────┐     ┌──────────────┐   ┌──────────┐  │
│  │  Monitoring DB  │     │ LLM Service  │   │ Config   │  │
│  │  (In-Memory +   │     │ (Groq API)   │   │ Manager  │  │
│  │   File Log)     │     │              │   │          │  │
│  ├─────────────────┤     ├──────────────┤   ├──────────┤  │
│  │ • Deque Storage │     │ • Analysis   │   │ • ENV    │  │
│  │ • Thread-Safe   │     │ • Insights   │   │ • Thresholds
│  │ • Querying      │     │ • Findings   │   │ • Feature │  │
│  │ • Filtering     │     │ • Recommend. │   │   Flags  │  │
│  │ • Statistics    │     │              │   │          │  │
│  │ • Persistence   │     │              │   │          │  │
│  └─────────────────┘     └──────────────┘   └──────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. API Layer (`app/api/routes.py`)
**Responsibility**: HTTP request handling and routing

**Key Endpoints**:
- `POST /events` - Submit events for monitoring
- `GET /health` - Current system health status
- `GET /logs` - Query monitoring logs
- `POST /logs/query` - Advanced log querying
- `POST /analysis/llm` - Trigger LLM analysis
- `POST /analysis/re-evaluate` - Manual re-evaluation
- `GET /stats` - Monitoring statistics
- `POST /maintenance/cleanup` - Log maintenance

### 2. Monitoring Engine (`app/monitoring/engine.py`)
**Responsibility**: Core monitoring logic and rule-based detection

**Key Features**:
```
Rule-Based Detection:
├── Threshold Violations
│   ├── Response Time (>5000ms)
│   ├── CPU Usage (>90%)
│   ├── Memory Usage (>85%)
│   ├── Error Rate (>10%)
│   └── Latency (>3000ms)
│
├── Invalid Output Detection
│   ├── Null/None values
│   ├── "error" strings
│   └── Empty structures
│
├── Consistency Checks
│   ├── Status code vs response logic
│   ├── Field relationships
│   └── Data integrity
│
├── Silent Failure Detection
│   ├── Success but null result
│   ├── Processed but no output
│   └── Completed but zero items
│
└── Anomaly Detection
    ├── Z-score analysis (>3 = anomaly)
    ├── Historical trends
    └── Pattern deviation
```

**Severity Scoring**:
- Invalid Output: +0.3
- Threshold Violation: +0.25 per violation
- Consistency Issue: +0.2
- Anomaly Detected: +0.1
- Silent Failure: +0.4

### 3. LLM Service (`app/services/groq_service.py`)
**Responsibility**: Optional intelligent analysis via Groq API

**Features**:
- Analyzes recent monitoring logs
- Detects patterns and trends
- Classifies severity (NORMAL/WARNING/CRITICAL)
- Provides human-readable insights
- Suggests corrective actions
- Provides confidence scoring

**Configuration**:
- `ENABLE_LLM_MONITORING`: Toggle on/off
- `GROQ_API_KEY`: API credentials
- `GROQ_MODEL`: Model selection
- `GROQ_MAX_TOKENS`: Response length

### 4. Monitoring Database (`app/utils/database.py`)
**Responsibility**: Log storage and retrieval

**Features**:
- In-memory deque storage (thread-safe)
- File persistence for durability
- Configurable size limits
- Efficient filtering and querying
- Statistics generation
- Automatic cleanup

**Data Model**:
```
MonitoringLog
├── event_id: str (unique identifier)
├── timestamp: datetime
├── source: str (data origin)
├── event_type: str (event classification)
├── input_snapshot: dict (raw input data)
├── monitoring_result: MonitoringResult
│   ├── status: HealthStatus
│   ├── severity_score: float (0.0-1.0)
│   ├── reasoning: str
│   ├── detected_issues: list[str]
│   ├── suggestions: list[str]
│   └── failed_rules: list[str]
└── llm_analysis: dict (optional)
```

### 5. Configuration Management (`app/config.py`)
**Responsibility**: Application settings and environment handling

**Key Settings**:
```
FastAPI Configuration
├── APP_NAME, APP_VERSION
├── DEBUG, HOST, PORT
└── Logging paths

Monitoring Configuration
├── ENABLE_LLM_MONITORING
├── WARNING_THRESHOLD (0.7)
└── CRITICAL_THRESHOLD (0.9)

Groq Configuration
├── GROQ_API_KEY
├── GROQ_MODEL
└── GROQ_MAX_TOKENS

Logging Configuration
├── LOG_LEVEL
└── LOG_FILE

Data Retention
└── MAX_LOG_ENTRIES (10,000)
```

### 6. Data Models (`app/models/schemas.py`)
**Responsibility**: Type safety with Pydantic schemas

**Key Models**:
- `EventRequest`: Input for submitting events
- `MonitoringResult`: Analysis result
- `MonitoringLog`: Complete log entry
- `HealthStatusResponse`: Health status response
- `LogsResponse`: Paginated log response
- `LLMAnalysisResponse`: LLM analysis output

## Data Flow

### Event Submission Flow
```
1. Client submits EventRequest to POST /events
2. API generates unique event_id
3. MonitoringEngine.analyze() processes event:
   - Applies all detection rules
   - Calculates severity score
   - Determines health status
   - Generates reasoning and suggestions
4. MonitoringLog created with results
5. Database stores log (memory + file)
6. Response returned to client
```

### Health Status Query Flow
```
1. Client requests GET /health
2. Database retrieves recent logs (last 100)
3. Aggregate status calculation:
   - If any CRITICAL → CRITICAL
   - Else if any WARNING → WARNING
   - Else → NORMAL
4. Calculate average severity score
5. Extract recent issues
6. Return HealthStatusResponse
```

### LLM Analysis Flow
```
1. Client requests POST /analysis/llm with lookback_minutes
2. Database retrieves recent logs
3. LLMService.analyze_logs() invoked:
   - Build analysis prompt from logs
   - Call Groq API
   - Parse response structure
   - Extract findings and recommendations
4. Return structured analysis
```

## Decision Logic - Fail-Safe Actions

Based on monitoring results, system can determine actions:

```
Status: NORMAL
└─ Action: CONTINUE
   └─ Normal operation continues

Status: WARNING
├─ Rule: Threshold approaching
└─ Action: RETRY or CONTINUE
   ├─ RETRY: Attempt operation again
   └─ CONTINUE: Proceed with caution

Status: CRITICAL
├─ Rule: Multiple failures detected
└─ Action: ESCALATE, REPROCESS, or HALT
   ├─ ESCALATE: Alert human operators
   ├─ REPROCESS: Reprocess failed data
   └─ HALT: Stop system flow immediately
```

## Extension Points

The system is designed for extensibility:

### Adding New Rules
1. Add detection method to `MonitoringEngine`
2. Update severity scoring logic
3. Add to `failed_rules` list
4. Update `_generate_suggestions()` for actions

### Adding New Metrics
1. Add metric threshold to `_check_threshold_violations()`
2. Update anomaly detection logic
3. Document in README

### Custom LLM Behavior
1. Modify prompt in `_build_analysis_prompt()`
2. Adjust parsing in `_parse_llm_response()`
3. Customize response fields

### Database Persistence
1. Implement persistent store (PostgreSQL, MongoDB)
2. Replace deque with database queries
3. Add migrations for schema changes

## Security Considerations

- **API Keys**: Stored in environment variables, never in code
- **CORS**: Currently permissive; restrict to known domains in production
- **Input Validation**: Pydantic handles all input validation
- **Error Handling**: Errors logged without exposing sensitive data
- **Logging**: Can be configured to mask sensitive data
- **Rate Limiting**: Can be added via middleware

## Performance Characteristics

- **Memory**: ~10KB per log entry
- **Max Logs**: 10,000 (configurable)
- **Query Speed**: O(n) for filters (acceptable for in-memory)
- **Detection Speed**: <10ms per event
- **LLM Latency**: ~1-5 seconds (network dependent)

## Deployment Considerations

### Development
```bash
python main.py
```

### Production
```bash
# Use Gunicorn with Uvicorn workers
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Scaling
- Load balance with multiple instances
- Implement persistent database
- Add message queue for async processing
- Deploy LLM service separately if needed

## Testing Strategy

### Unit Tests
- MonitoringEngine rule detection
- Severity score calculations
- Database operations

### Integration Tests
- Full event submission workflow
- LLM integration
- API endpoints

### Load Tests
- Event submission throughput
- Log query performance
- Memory stability

## Monitoring the Monitor

Meta-monitoring considerations:

1. **Health Checks**:
   - Disk space for logs
   - Memory usage
   - API response times

2. **Alerts**:
   - Database approaching max entries
   - LLM API failures
   - System resource constraints

3. **Metrics**:
   - Events processed per minute
   - Average detection latency
   - LLM analysis success rate

## Future Enhancements

1. **Persistence Layer**
   - PostgreSQL for durable storage
   - Time-series database for metrics

2. **Advanced Analytics**
   - Machine learning for pattern detection
   - Forecasting anomalies
   - Clustering similar issues

3. **Multi-Tenancy**
   - Tenant isolation
   - Custom rule sets per tenant
   - Usage billing

4. **User Interface**
   - Dashboard for visualization
   - Alert configuration UI
   - Custom rule builder

5. **Integration**
   - Webhook notifications
   - Slack/PagerDuty integration
   - Custom action plugins

---

**Architecture Version**: 1.0.0
**Last Updated**: 2025-01-30
