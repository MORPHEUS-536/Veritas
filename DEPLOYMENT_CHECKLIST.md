# PostgreSQL via NeonDB Integration - Deployment Checklist

## Pre-Deployment Checklist

### [ ] Environment Setup
- [ ] NeonDB account created (https://neon.tech)
- [ ] Project created in NeonDB
- [ ] Connection string copied
- [ ] `.env` file created in Veritas root
- [ ] DATABASE_URL set correctly in .env
- [ ] .env added to .gitignore (don't commit)

### [ ] Dependencies Installation
- [ ] Monitoring2.0: `pip install -r requirements.txt`
- [ ] staffstuddash: `pip install -r requirements.txt`
- [ ] dropout: `pip install sqlalchemy psycopg2-binary python-dotenv`
- [ ] All packages installed without errors

### [ ] Database Verification
- [ ] Run `python verify_database.py`
- [ ] ✓ PostgreSQL connection successful
- [ ] ✓ Monitoring2.0 tables created
- [ ] ✓ staffstuddash database initialized
- [ ] ✓ Dropout database initialized

### [ ] Code Review
- [ ] `Monitoring2.0/backend/app/utils/database.py` verified
- [ ] `staffstuddash/backend/datastore.py` verified
- [ ] `dropout/database.py` verified
- [ ] All SQLAlchemy models verified
- [ ] Configuration files updated

### [ ] Testing
- [ ] Monitoring2.0 backend starts: `python main.py`
- [ ] staffstuddash backend starts: `python main.py`
- [ ] dropout system initializes correctly
- [ ] API endpoints responding
- [ ] Database operations working

### [ ] Documentation
- [ ] README_DATABASE_INTEGRATION.md reviewed
- [ ] DATABASE_SETUP.md reviewed
- [ ] ARCHITECTURE.md reviewed
- [ ] QUICK_REFERENCE.md bookmarked
- [ ] Team notified of changes

---

## Deployment Checklist

### [ ] Pre-Production Testing
- [ ] Test with sample data load
- [ ] Test query performance
- [ ] Test with multiple concurrent requests
- [ ] Test fallback mode (disconnect DB temporarily)
- [ ] Test error handling

### [ ] Production Configuration
- [ ] DATABASE_URL set in production environment
- [ ] Using production-tier NeonDB project
- [ ] SSL enabled (sslmode=require)
- [ ] DEBUG=False in production
- [ ] LOG_LEVEL set appropriately

### [ ] Security
- [ ] DATABASE_URL secured (not in git)
- [ ] Credentials managed by secrets manager
- [ ] SSL certificate validation enabled
- [ ] No hardcoded passwords in code
- [ ] Connection strings encrypted in transit

### [ ] Monitoring Setup
- [ ] Database connection monitoring enabled
- [ ] Query performance monitoring
- [ ] Error logging configured
- [ ] Backup verification
- [ ] Alert thresholds set

### [ ] Backup & Recovery
- [ ] NeonDB backup enabled
- [ ] Backup retention policy set
- [ ] Recovery procedure documented
- [ ] Test restore from backup
- [ ] Disaster recovery plan in place

### [ ] Deployment
- [ ] Code deployed to production
- [ ] Environment variables configured
- [ ] Database migrations (if any) applied
- [ ] Systemd/supervisor configured (if needed)
- [ ] Health checks passing

### [ ] Post-Deployment
- [ ] Monitor application logs
- [ ] Check database metrics
- [ ] Verify data persistence
- [ ] Test all API endpoints
- [ ] Confirm user data in database
- [ ] Set up performance monitoring

---

## Rollback Procedure

If issues occur:

### Quick Rollback (In-Memory Mode)
```bash
# Remove or comment out DATABASE_URL
# unset DATABASE_URL
# Application falls back to in-memory automatically
```

### Full Rollback (Previous Version)
```bash
# If using git
git revert <commit-hash>
# Redeploy previous version
```

### Data Recovery
```bash
# If data corruption suspected
# Restore from NeonDB backup
# Contact NeonDB support if needed
```

---

## Post-Integration Verification

### Daily Checks (First Week)
- [ ] Check application logs for errors
- [ ] Verify database connection stability
- [ ] Monitor query performance
- [ ] Check data persistence
- [ ] Verify backup completion

### Weekly Checks (Ongoing)
- [ ] Review database size
- [ ] Check query performance trends
- [ ] Verify backup integrity
- [ ] Review error logs
- [ ] Check connection statistics

### Monthly Checks
- [ ] Database optimization review
- [ ] Index performance analysis
- [ ] Archive old data (if needed)
- [ ] Security audit
- [ ] Capacity planning

---

## Troubleshooting Guide

### Connection Issues

**Problem**: `could not connect to server: Connection refused`
```bash
# Solution
1. Check DATABASE_URL format
2. Verify NeonDB project is running
3. Check network connectivity
4. Test with: python verify_database.py
```

**Problem**: `SSL: CERTIFICATE_VERIFY_FAILED`
```bash
# Solution
1. Add ?sslmode=require to DATABASE_URL
2. Ensure NeonDB connection string includes SSL
3. Update psycopg2: pip install --upgrade psycopg2-binary
```

**Problem**: `OperationalError: timeout expired`
```bash
# Solution
1. Add ?connect_timeout=10 to DATABASE_URL
2. Check Neon connection quota
3. Reduce concurrent connections
4. Increase NeonDB resource allocation
```

### Performance Issues

**Problem**: `Slow queries`
```python
# Solution
1. Enable SQL logging: DEBUG=True
2. Check query execution with EXPLAIN ANALYZE
3. Add indexes to frequently queried columns
4. Use batch operations instead of single inserts
```

**Problem**: `High CPU usage on database`
```bash
# Solution
1. Check for long-running queries
2. Kill idle connections
3. Optimize slow queries
4. Increase NeonDB resources
```

### Data Issues

**Problem**: `Missing data after restart`
```bash
# Solution
1. Check if using in-memory fallback
2. Verify DATABASE_URL is set
3. Check database connectivity
4. Restore from backup if needed
```

---

## Monitoring Commands

### Check Database Status
```bash
# Test connection
python -c "from shared_db_utils import db_manager; print('Connected!')"

# Run verification
python verify_database.py

# Check specific backend
cd Monitoring2.0/backend && python -c "from app.utils.database import monitoring_db; print(monitoring_db.get_statistics())"
```

### Query Database Directly
```bash
# Using psql (if installed)
psql postgresql://user:password@host/db

# Check tables
SELECT table_name FROM information_schema.tables WHERE table_schema='public';

# Check record counts
SELECT 'monitoring_logs' as table_name, COUNT(*) as row_count FROM monitoring_logs
UNION ALL
SELECT 'students', COUNT(*) FROM students;
```

### View Logs
```bash
# Application logs
tail -f logs/app.log

# NeonDB connection logs
grep -i "database\|postgres\|connection" logs/app.log

# Performance logs
grep -i "slow\|timeout\|error" logs/app.log
```

---

## Performance Optimization

### After Initial Deployment

1. **Add Indexes**
```sql
CREATE INDEX idx_student_email ON students(email);
CREATE INDEX idx_logs_created ON monitoring_logs(created_at);
CREATE INDEX idx_assessment_student ON assessment_logs(student_id);
```

2. **Analyze Query Plans**
```sql
EXPLAIN ANALYZE
SELECT * FROM monitoring_logs WHERE source='api' ORDER BY timestamp DESC LIMIT 100;
```

3. **Optimize Connections**
- Monitor connection pool usage
- Adjust connection timeout settings
- Use connection pooling if multiple instances

4. **Data Maintenance**
- Archive old logs periodically
- Vacuum tables to reclaim space
- Update statistics for query optimizer

---

## Team Communication

### Notify Team About

- [ ] Database now uses PostgreSQL (not in-memory)
- [ ] All data is persistent
- [ ] DATABASE_URL must be set
- [ ] Data is backed up automatically
- [ ] Query performance improved

### Documentation to Share

- [ ] `README_DATABASE_INTEGRATION.md` - Overview
- [ ] `DATABASE_SETUP.md` - Setup guide
- [ ] `QUICK_REFERENCE.md` - Common operations
- [ ] `ARCHITECTURE.md` - Technical details

### Training Points

- [ ] How to use database (API unchanged)
- [ ] Where to find data persistence documentation
- [ ] How to troubleshoot issues
- [ ] Where to get help

---

## Success Criteria

✅ All checks pass:
- [ ] Application starts without errors
- [ ] Database tables created successfully
- [ ] Data persists across application restarts
- [ ] API endpoints work as before
- [ ] No performance degradation
- [ ] Backups working automatically
- [ ] Monitoring and alerts configured
- [ ] Team trained and informed

---

## Sign-Off

- **Deployment Date**: _____________
- **Deployed By**: _____________
- **Verified By**: _____________
- **Notes**: _____________

---

## Contact & Support

For issues or questions:
1. Check `DATABASE_SETUP.md` first
2. Run `python verify_database.py`
3. Review logs in `logs/app.log`
4. Check NeonDB dashboard status
5. Contact development team

---

**Integration Status**: ✅ Ready for Production
**Last Updated**: January 31, 2026
