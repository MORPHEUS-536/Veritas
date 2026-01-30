# NeonDB Connection - Visual Guide

## 🎯 Complete Setup in 7 Steps

---

## **STEP 1: Create NeonDB Account**

```
┌─────────────────────────────────────┐
│   Visit: https://neon.tech          │
│                                      │
│   [Sign Up Button]                   │
│   ↓                                  │
│   Enter Email                        │
│   Enter Password                     │
│   Enter Organization Name            │
│   ↓                                  │
│   ✓ Email Verified                   │
└─────────────────────────────────────┘

Time: 5 minutes
Result: Account created ✓
```

---

## **STEP 2: Create Project**

```
┌─────────────────────────────────────┐
│   NeonDB Dashboard                   │
│                                      │
│   [Create a project]                 │
│   ├─ Project name: Veritas           │
│   ├─ Region: US East (N. Virginia)   │
│   └─ [Create Project]                │
│       ↓                              │
│       ⏳ Initializing...              │
│       ↓                              │
│       ✓ Project Ready                │
└─────────────────────────────────────┘

Time: 2 minutes
Result: Project created ✓
```

---

## **STEP 3: Get Connection String**

```
┌──────────────────────────────────────────────────┐
│   NeonDB Project Dashboard                       │
│                                                   │
│   ┌─ Connection Strings                          │
│   │                                              │
│   │  postgresql://neonuser:abcd1234@           │
│   │  ep-cool-flower-12345.us-east-1.neon.tech   │
│   │  /neondb                                     │
│   │                                              │
│   │  [Copy] ← CLICK THIS                        │
│   │                                              │
│   └─ Copied! ✓                                   │
│                                                   │
└──────────────────────────────────────────────────┘

Time: 1 minute
Result: String copied ✓
```

---

## **STEP 4: Update .env File**

```
FILE: Veritas/.env

BEFORE:
────────────────────────────
# (empty or old value)


AFTER:
────────────────────────────
DATABASE_URL=postgresql://neonuser:abcd1234@ep-cool-flower-12345.us-east-1.neon.tech/neondb?sslmode=require
                ↑                                                                                    ↑
         Your NeonDB string from Step 3                                    Add this for SSL security


Time: 1 minute
Result: .env updated ✓
```

---

## **STEP 5: Install Dependencies**

```
Terminal / PowerShell

Command 1:
$ cd Monitoring2.0/backend
$ pip install -r requirements.txt
  → Installing sqlalchemy
  → Installing psycopg2-binary
  → Installing other packages
  ✓ Successfully installed

Command 2:
$ cd ../../staffstuddash/backend
$ pip install -r requirements.txt
  ✓ Successfully installed

Command 3:
$ cd ../../dropout
$ pip install sqlalchemy psycopg2-binary python-dotenv
  ✓ Successfully installed


Time: 3 minutes
Result: All packages installed ✓
```

---

## **STEP 6: Verify Connection**

```
Terminal / PowerShell

$ python verify_database.py

════════════════════════════════════════════════════
         Veritas Backend Database Verification
════════════════════════════════════════════════════

[1] Testing NeonDB PostgreSQL Connection...
    Connection String: postgresql://***:***@ep-cool-flower-...
    ✓ PostgreSQL connection successful

[2] Testing Monitoring2.0 Database Models...
    ✓ Monitoring2.0 tables created/verified

[3] Testing staffstuddash Database Models...
    ✓ staffstuddash database connected

[4] Testing Dropout Detection Database Models...
    ✓ Dropout database initialized

════════════════════════════════════════════════════
Summary
════════════════════════════════════════════════════
PostgreSQL Connection: ✓ PASSED
Monitoring2.0: ✓ PASSED
staffstuddash: ✓ PASSED
Dropout Detection: ✓ PASSED

✓ All tests passed! Database setup is complete.

Your backends are ready to use PostgreSQL via NeonDB!
════════════════════════════════════════════════════

Time: 1 minute
Result: All connections verified ✓
```

---

## **STEP 7: Start Your Backend**

```
Terminal / PowerShell - Window 1

$ cd Monitoring2.0/backend
$ python main.py

2026-01-31 14:32:45 - INFO - ============================================================
2026-01-31 14:32:45 - INFO - Starting Monitoring System Backend v1.0.0
2026-01-31 14:32:45 - INFO - ============================================================
2026-01-31 14:32:45 - INFO - Configuration validated successfully
2026-01-31 14:32:45 - INFO - Database initialized
2026-01-31 14:32:45 - INFO - Application running on 0.0.0.0:8000
2026-01-31 14:32:45 - INFO - ============================================================

✓ Ready to accept requests!


Terminal / PowerShell - Window 2

$ cd staffstuddash/backend
$ python main.py

info:     Uvicorn running on http://0.0.0.0:8000
info:     Application startup complete
info:     Database connection status: PostgreSQL via NeonDB

✓ Backend is running!

Time: 2 minutes
Result: Backends started ✓
```

---

## 🎉 Success!

```
┌──────────────────────────────────────────────────┐
│                                                   │
│  ✓ NeonDB Account Created                        │
│  ✓ Project Created                               │
│  ✓ Connection String Obtained                    │
│  ✓ .env File Updated                             │
│  ✓ Dependencies Installed                        │
│  ✓ Connection Verified                           │
│  ✓ Backends Running                              │
│                                                   │
│  🎯 All Systems Connected to PostgreSQL!         │
│                                                   │
│  Your data is now:                               │
│  ✓ Persistent (survives restarts)                │
│  ✓ Backed up (automatic daily)                   │
│  ✓ Secure (SSL encrypted)                        │
│  ✓ Scalable (unlimited records)                  │
│                                                   │
└──────────────────────────────────────────────────┘

Total Time: ~15 minutes
Ready for Production: YES ✓
```

---

## 📊 Architecture Overview

```
Your Application
        ↓
   ┌────┴─────┐
   ↓          ↓
Monitoring  staffstuddash  dropout
   ↓          ↓              ↓
   └────┬──────┴──────┬──────┘
        ↓             ↓
   .env file    DATABASE_URL
        ↓             ↓
   SQLAlchemy ←──────┘
        ↓
   psycopg2 (PostgreSQL Driver)
        ↓
   ┌─────────────────────────┐
   │   NeonDB PostgreSQL     │
   │   (Cloud Database)      │
   │                         │
   │  15 Tables:             │
   │  ✓ Persistent Storage   │
   │  ✓ Automatic Backups    │
   │  ✓ SSL Encrypted        │
   │  ✓ Scalable             │
   └─────────────────────────┘
```

---

## 🚨 Common Issues & Solutions

### Issue 1: Connection Refused
```
Error: could not connect to server: Connection refused

Solution:
1. Check .env has DATABASE_URL
2. Verify string is copied correctly
3. Make sure ?sslmode=require is at the end
4. Run: python verify_database.py
```

### Issue 2: SSL Error
```
Error: SSL: CERTIFICATE_VERIFY_FAILED

Solution:
Add to DATABASE_URL: ?sslmode=require

Example:
postgresql://user:pass@ep-xxxxx.neon.tech/neondb?sslmode=require
                                                   ↑
                                            Add this part
```

### Issue 3: Timeout Error
```
Error: timeout expired

Solution:
Add timeout to DATABASE_URL: ?connect_timeout=10

Example:
postgresql://user:pass@ep-xxxxx.neon.tech/neondb?sslmode=require&connect_timeout=10
```

---

## ✅ Final Checklist

Before saying "Setup Complete", verify:

- [ ] **NeonDB Account**: Can log in at https://neon.tech
- [ ] **Project Created**: See it in NeonDB dashboard
- [ ] **Connection String**: Copied from NeonDB
- [ ] **.env Updated**: DATABASE_URL set with ?sslmode=require
- [ ] **Dependencies**: `pip install -r requirements.txt` successful
- [ ] **Verification**: `python verify_database.py` shows all ✓
- [ ] **Backends Starting**: `python main.py` runs without errors
- [ ] **Data Persistent**: Data survives app restart

If all ✓, you're done! 🎉

---

## 📚 Reference Files

```
Veritas/
├── .env ← Your configuration (DO NOT COMMIT)
├── NEONDB_QUICK_START.md ← This guide
├── DATABASE_SETUP.md ← Detailed setup
├── QUICK_REFERENCE.md ← Quick lookup
├── verify_database.py ← Connection tester
├── setup.bat ← Automated setup (Windows)
└── setup.sh ← Automated setup (Linux/Mac)
```

---

**You're all set! Your backends are now connected to PostgreSQL via NeonDB.** 🚀

All your data is persistent, backed up, and secure! 🔒
