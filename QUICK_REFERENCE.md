# Quick Reference - NeonDB PostgreSQL Integration

## 🚀 Quick Start (5 minutes)

### 1. Get Connection String
```
https://neon.tech → Sign up → Create Project → Copy Connection String
```

### 2. Configure .env
```bash
# /Veritas/.env
DATABASE_URL=postgresql://user:password@ep-xxxxx.neon.tech/neondb?sslmode=require
```

### 3. Run Setup
```bash
# Windows
setup.bat

# Linux/Mac
bash setup.sh

# Manual
pip install -r requirements.txt
python verify_database.py
```

## 📚 Database URLs

### NeonDB (Production)
```
postgresql://user:password@ep-xxxxx.neon.tech/neondb?sslmode=require
```

### Local PostgreSQL (Development)
```
postgresql://postgres:password@localhost:5432/veritas_db
```

## 🔌 Code Usage Examples

### Monitoring2.0
```python
from app.utils.database import monitoring_db

# Add log
monitoring_db.add_log(log_object)

# Query logs
logs, total = monitoring_db.get_logs(source="api", limit=100)

# Get stats
stats = monitoring_db.get_statistics()
```

### staffstuddash
```python
from datastore import datastore

# Add student
datastore.add_student("s001", "Name", "email@example.com")

# Add assessment
datastore.add_assessment("s001", "exam", "Math", 85.0)

# Get performance
perf = datastore.get_performance_record("s001")
```

### dropout
```python
from database import db_manager

# Add student
db_manager.add_student("s001", "Name", "email@example.com")

# Add event
db_manager.add_learning_event("evt001", "s001", "q123", "QUESTION_SUBMIT")

# Save prediction
db_manager.save_prediction("pred001", "s001", "COGNITIVE", 0.75, "HIGH")
```

## 📊 Database Tables

### Monitoring2.0
- `monitoring_logs` - Individual log entries
- `monitoring_results` - Analysis results
- `system_health` - Overall health status

### staffstuddash
- `students` - Student profiles
- `drafts` - Student submissions
- `assessment_logs` - Test results
- `performance_records` - Analytics
- `action_logs` - Audit trail
- `concept_modules` - Learning concepts

### dropout
- `dropout_students` - Student records
- `dropout_learning_events` - Activity events
- `dropout_attempt_history` - Question attempts
- `dropout_assessments` - Test results
- `dropout_feature_sets` - ML features
- `dropout_predictions` - Predictions

## ⚙️ Configuration

### Required Environment Variable
```
DATABASE_URL=postgresql://...
```

### Optional
```
DEBUG=False              # SQL logging
HOST=0.0.0.0           # Server host
PORT=8000              # Server port
LOG_LEVEL=INFO         # Log level
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check DATABASE_URL and PostgreSQL status |
| SSL error | Add `?sslmode=require` to URL |
| Table exists error | Normal - tables only created once |
| Fallback mode | Database unavailable - check URL |
| Timeout | Add `?connect_timeout=10` to URL |

## 📁 Key Files

| File | Purpose |
|------|---------|
| `.env` | Configuration (DO NOT COMMIT) |
| `DATABASE_SETUP.md` | Full setup guide |
| `IMPLEMENTATION_SUMMARY.md` | Implementation details |
| `verify_database.py` | Connection test script |
| `setup.bat / setup.sh` | Automated setup |

## 🔗 Links

- **NeonDB**: https://neon.tech
- **PostgreSQL**: https://www.postgresql.org
- **SQLAlchemy**: https://docs.sqlalchemy.org
- **psycopg2**: https://www.psycopg.org

## ✅ Verification

```bash
# Test database connection
python verify_database.py

# Should show:
# ✓ PostgreSQL connection successful
# ✓ Monitoring2.0 tables created
# ✓ staffstuddash database initialized
# ✓ Dropout database initialized
```

## 🎯 What Changed

✓ Monitoring2.0: In-memory → PostgreSQL
✓ staffstuddash: Dict/List → SQLAlchemy ORM
✓ dropout: No storage → PostgreSQL models
✓ All code logic: **UNCHANGED**
✓ All APIs: **UNCHANGED**
✓ Backward compatibility: **MAINTAINED**

## 📝 Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Test connection
python verify_database.py

# Start Monitoring2.0
cd Monitoring2.0/backend && python main.py

# Start staffstuddash
cd staffstuddash/backend && python main.py

# View logs
tail -f logs/app.log
```

## 🔒 Security Checklist

- [ ] DATABASE_URL set in .env (not committed)
- [ ] Using `?sslmode=require` for NeonDB URLs
- [ ] .env in .gitignore
- [ ] Connection string treated as secret
- [ ] No hardcoded credentials

## 📞 Need Help?

1. Check `DATABASE_SETUP.md` for detailed documentation
2. Run `verify_database.py` to diagnose issues
3. Check logs for error messages
4. Ensure DATABASE_URL is correct
5. Test PostgreSQL connectivity manually

---

**Status**: ✅ All backends configured for PostgreSQL via NeonDB
**Impact**: Zero impact on application logic - database transparent to code
**Next Step**: Update DATABASE_URL in .env and run setup.bat/setup.sh
