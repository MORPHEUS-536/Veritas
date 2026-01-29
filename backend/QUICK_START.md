# 🚀 Veritas Backend - Quick Start Guide

Get your backend running with Neon DB in **3 minutes** or **local setup in 5 minutes**.

---

## ⚡ Express Setup (3 Minutes with Neon DB)

### Step 1: Create Neon Account & Database (2 min)

1. Go to https://console.neon.tech/
2. Click "Sign Up" (free tier available)
3. Create a new project (name it "veritas" or similar)
4. Wait for project to be created
5. Click "Connection string" tab
6. Copy the connection string (looks like: `postgresql://user:password@host/database?sslmode=require`)

### Step 2: Configure Backend (1 min)

```bash
# 1. Set environment variable
export DATABASE_URL="postgresql://neondb_owner:npg_B0pdeQuPm9oN@ep-withered-salad-a1zcgmjf-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# 2. Install dependencies
pip install -r requirements_db.txt

# 3. Initialize database
python -c "from database import init_db; init_db()"

# 4. Start backend
uvicorn api_routes:app --reload
```

### Step 3: Verify Installation

Open http://localhost:8000/docs in your browser → See Swagger UI with all endpoints

✅ **Done!** Backend is running with Neon DB

---

## 🐍 Local Setup (5 Minutes with Local PostgreSQL)

### Prerequisites

- Python 3.9+
- PostgreSQL 13+

### Step 1: Install PostgreSQL

**Windows:** Download from https://www.postgresql.org/download/windows/
**Mac:** `brew install postgresql@15`
**Linux:** `sudo apt-get install postgresql postgresql-contrib`

### Step 2: Create Database

```bash
# Login to PostgreSQL
psql -U postgres

# In PostgreSQL prompt:
CREATE DATABASE veritas_db;
\q
```

### Step 3: Configure Backend

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Update .env with your PostgreSQL connection
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/veritas_db

# 3. Install dependencies
pip install -r requirements_db.txt

# 4. Initialize database
python -c "from database import init_db; init_db()"

# 5. Start backend
uvicorn api_routes:app --reload
```

### Step 4: Verify Installation

Open http://localhost:8000/docs → See Swagger UI

---

## 🔧 Automated Setup

### Windows PowerShell

```powershell
# Run setup wizard
.\setup_windows.ps1

# Or with Neon DB URL
.\setup_windows.ps1 -DatabaseUrl "postgresql://..."
```

### Linux/Mac

```bash
# Make executable and run
chmod +x setup.sh
./setup.sh
```

---

## 📋 Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Required: Neon DB connection string
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# Security: Change in production!
JWT_SECRET=your-secret-key-min-32-chars

# Optional: Debug mode
DEBUG=True
```

See `.env.example` for all available options.

---

## ✅ Verify Everything Works

```bash
# Test database connection
python test_neon_connection.py

# Test API endpoints (in another terminal)
curl http://localhost:8000/health
```

Expected output: `{"status": "ok"}`

---

## 📱 Test Backend API

### Register a Student

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "username": "student1",
    "password": "secure123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "secure123"
  }'
```

Response includes `access_token` - use it for authenticated requests:

```bash
curl -X GET http://localhost:8000/student/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🐛 Troubleshooting

### Connection Refused

**Problem:** `Connection refused - could not connect to server`

**Solution:**
1. Verify DATABASE_URL is set: `echo $DATABASE_URL` (Linux/Mac) or `echo %DATABASE_URL%` (Windows)
2. Check if Neon project is running: https://console.neon.tech
3. Verify internet connection
4. Try `python test_neon_connection.py` for diagnostics

### Authentication Failed

**Problem:** `FATAL: password authentication failed`

**Solution:**
1. Check username/password in connection string
2. Regenerate connection string in Neon console
3. Copy exact string (avoid extra spaces)

### SSL Certificate Error

**Problem:** `SSL connection error`

**Solution:**
1. Ensure connection string includes `?sslmode=require`
2. For Neon: Verify endpoint is in correct region
3. Try updating psycopg2: `pip install --upgrade psycopg2-binary`

### Port Already In Use

**Problem:** `Address already in use`

**Solution:**
```bash
# Change port
uvicorn api_routes:app --port 8001

# Or kill existing process
# Windows: netstat -ano | findstr :8000
# Linux/Mac: lsof -i :8000 | kill -9 PID
```

---

## 📊 Monitoring

### Neon DB Console

Visit https://console.neon.tech to:
- View active connections
- Check query performance
- Monitor compute usage
- Review branch/backup history

### Backend Logs

```bash
# Enable SQL query logging
export SQLALCHEMY_ECHO=1
uvicorn api_routes:app --reload

# Check test results
python test_neon_connection.py
```

---

## 🔒 Production Deployment

### Before Going Live

1. **Update JWT_SECRET**: Generate new 32+ character secret
2. **Set DEBUG=False**
3. **Use strong database password**
4. **Enable HTTPS**
5. **Configure CORS** for your domain
6. **Set up monitoring** in Neon console
7. **Enable backups** in Neon (automatic in Pro tier)

See **DEPLOYMENT.md** for complete production guide.

---

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design & database schema
- **[NEON_DB_SETUP.md](NEON_DB_SETUP.md)** - Detailed Neon integration
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[README.md](README.md)** - Full feature overview

---

## 🆘 Need Help?

1. **Check documentation**: NEON_DB_SETUP.md for Neon-specific help
2. **Run test script**: `python test_neon_connection.py`
3. **View logs**: Check terminal output when starting backend
4. **Verify environment**: `python -c "import database, sqlalchemy; print('OK')"`

---

## ✨ Next Steps

✅ Backend running  
✅ Database configured  
✅ API endpoints available  

**What's next:**

1. Connect frontend to API endpoints (see [ARCHITECTURE.md](ARCHITECTURE.md))
2. Test exam creation and student submissions
3. Set up monitoring and analytics
4. Configure additional features (Redis caching, email, etc.)

---

**Version:** 1.0  
**Last Updated:** 2024  
**Backend:** Python 3.9+ | FastAPI | SQLAlchemy | PostgreSQL/Neon
