# NeonDB Connection Instructions

## Step-by-Step Guide to Connect NeonDB

### **Step 1: Create NeonDB Account** (5 minutes)

1. Go to **https://neon.tech**
2. Click **Sign Up** (top right)
3. Sign up with:
   - Email address
   - Password
   - Organization name (e.g., "Veritas")
4. Verify your email
5. You're in! ✓

---

### **Step 2: Create a Project in NeonDB** (2 minutes)

1. After login, you'll see **"Create a project"** button
2. Fill in:
   - **Project name**: `Veritas` (or any name)
   - **Region**: `US East (N. Virginia)` (recommended for lowest latency)
   - Click **Create Project**
3. Wait for project to initialize (30 seconds)
4. You're done! ✓

---

### **Step 3: Get Your Connection String** (1 minute)

1. After project creation, you'll see the dashboard
2. Look for the **Connection String** section
3. You'll see something like:
   ```
   postgresql://user:password@ep-projectname.us-east-1.neon.tech/neondb
   ```
4. **Copy the entire string** ✓

---

### **Step 4: Update Your .env File** (1 minute)

1. Open file: `Veritas/.env`
2. Find or add this line:
   ```
   DATABASE_URL=postgresql://user:password@ep-projectname.us-east-1.neon.tech/neondb?sslmode=require
   ```
3. **Paste your connection string** from Step 3
4. **Add `?sslmode=require`** at the end (for SSL security)
5. **Save the file** ✓

**Example:**
```env
DATABASE_URL=postgresql://neonuser:abc123@ep-cool-flower-123456.us-east-1.neon.tech/neondb?sslmode=require
```

---

### **Step 5: Install Dependencies** (3 minutes)

Open Terminal/PowerShell and run:

**For Monitoring2.0:**
```bash
cd Monitoring2.0/backend
pip install -r requirements.txt
cd ../..
```

**For staffstuddash:**
```bash
cd staffstuddash/backend
pip install -r requirements.txt
cd ../..
```

**For dropout:**
```bash
cd dropout
pip install sqlalchemy psycopg2-binary python-dotenv
cd ..
```

---

### **Step 6: Verify Connection** (1 minute)

Run the verification script:

```bash
python verify_database.py
```

**You should see:**
```
✓ PostgreSQL connection successful
✓ Monitoring2.0 tables created
✓ staffstuddash database initialized
✓ Dropout database initialized
```

If you see ✓ for all, **you're connected!** ✓

---

### **Step 7: Test Your Backend** (2 minutes)

**For Monitoring2.0:**
```bash
cd Monitoring2.0/backend
python main.py
```

**For staffstuddash:**
```bash
cd staffstuddash/backend
python main.py
```

You should see:
```
Application running on 0.0.0.0:8000
Database initialized
```

✓ **Success!**

---

## 🆘 Troubleshooting

### Error: "could not connect to server"

**Problem**: Connection string is wrong or NeonDB is down

**Solution**:
1. Check DATABASE_URL in .env
2. Make sure you copied it correctly from NeonDB dashboard
3. Verify the string includes `?sslmode=require`

**Test manually:**
```bash
python -c "from sqlalchemy import create_engine; create_engine(open('.env').read().split('=')[1]).connect()"
```

---

### Error: "SSL: CERTIFICATE_VERIFY_FAILED"

**Problem**: Missing SSL flag

**Solution**:
Make sure your DATABASE_URL ends with:
```
?sslmode=require
```

Should look like:
```
postgresql://user:pass@ep-xxxxx.neon.tech/neondb?sslmode=require
```

---

### Error: "timeout expired"

**Problem**: Connection timeout or NeonDB connection quota hit

**Solution**:
Add connection timeout to DATABASE_URL:
```
postgresql://user:pass@ep-xxxxx.neon.tech/neondb?sslmode=require&connect_timeout=10
```

---

### Message: "Using in-memory fallback"

**Problem**: Database not connecting but app still works

**Solution**:
1. Check if DATABASE_URL is set: `echo %DATABASE_URL%` (Windows)
2. Verify NeonDB is running: https://neon.tech/app/projects
3. Test connection: `python verify_database.py`

The app will work in memory mode, but data won't persist. Set DATABASE_URL to fix.

---

## ✅ Verification Checklist

- [ ] NeonDB account created
- [ ] Project created in NeonDB
- [ ] Connection string copied
- [ ] `.env` file has DATABASE_URL
- [ ] `?sslmode=require` added to URL
- [ ] Dependencies installed
- [ ] `python verify_database.py` shows ✓ for all
- [ ] Backend starts without errors
- [ ] Database tables created in NeonDB dashboard

---

## 📝 Quick Commands

```bash
# Test connection
python verify_database.py

# View your DATABASE_URL (for debugging)
echo %DATABASE_URL%  # Windows
echo $DATABASE_URL   # Linux/Mac

# Check if psycopg2 installed
pip list | grep psycopg2

# Start all backends
cd Monitoring2.0/backend && python main.py &
cd staffstuddash/backend && python main.py &
cd dropout && python main.py &
```

---

## 🔑 Key Points

✅ **DATABASE_URL is required** - App won't use PostgreSQL without it
✅ **?sslmode=require is important** - NeonDB requires secure connections
✅ **Never commit .env** - It has your password
✅ **Free tier available** - Start at $0/month
✅ **Automatic backups** - NeonDB backs up daily

---

## 📊 Connection Flow

```
Your Code (main.py)
    ↓
Environment Variable (DATABASE_URL from .env)
    ↓
SQLAlchemy Engine
    ↓
psycopg2 PostgreSQL Driver
    ↓
NeonDB PostgreSQL Server (Cloud)
    ↓
Your Data (Persistent Storage)
```

---

## 🎯 Common Connection Strings

### NeonDB (Production)
```
postgresql://user:password@ep-projectname.us-east-1.neon.tech/neondb?sslmode=require
```

### Local PostgreSQL (Development)
```
postgresql://postgres:password@localhost:5432/veritas_db
```

### Railway PostgreSQL
```
postgresql://user:password@region.railway.app:5432/railway?sslmode=require
```

---

## 📞 Need More Help?

1. **Check docs**: `DATABASE_SETUP.md`
2. **Run verification**: `python verify_database.py`
3. **View logs**: `logs/app.log`
4. **NeonDB Support**: https://neon.tech/docs
5. **PostgreSQL Help**: https://www.postgresql.org/docs/

---

## ⏱️ Time Estimate

| Step | Time |
|------|------|
| Create account | 5 min |
| Create project | 2 min |
| Get connection string | 1 min |
| Update .env | 1 min |
| Install dependencies | 3 min |
| Verify connection | 1 min |
| Test backend | 2 min |
| **Total** | **~15 minutes** |

---

**You're ready to go!** 🚀

After following these steps, your backends will be connected to NeonDB PostgreSQL with:
- ✅ Persistent data storage
- ✅ Automatic backups
- ✅ Secure encrypted connections
- ✅ Production-ready reliability

No code changes needed - your application works exactly the same!
