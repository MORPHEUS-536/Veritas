# 🔧 NeonDB Setup - 7 Simple Steps

## Copy & Paste Instructions

### **Step 1️⃣ : Sign Up**
```
Go to: https://neon.tech
→ Sign Up
→ Verify email
Done! ✓
```

---

### **Step 2️⃣ : Create Project**
- Click **"Create a project"**
- Name: `Veritas`
- Region: `US East (N. Virginia)`
- Click **"Create Project"**
- Wait 30 seconds
- Done! ✓

---

### **Step 3️⃣ : Copy Connection String**
- NeonDB Dashboard → Connection Strings section
- Copy entire string starting with `postgresql://`
- Should look like:
  ```
  postgresql://neonuser:password123@ep-cool-flower-12345.us-east-1.neon.tech/neondb
  ```
- Done! ✓

---

### **Step 4️⃣ : Update .env File**

**File Location**: `Veritas/.env`

**Add this line** (paste your connection string from Step 3):
```env
DATABASE_URL=postgresql://neonuser:password123@ep-cool-flower-12345.us-east-1.neon.tech/neondb?sslmode=require
```

**Important**: Add `?sslmode=require` at the end

Done! ✓

---

### **Step 5️⃣ : Install Packages**

**Run in Terminal/PowerShell:**

```bash
# For Monitoring2.0
cd Monitoring2.0/backend && pip install -r requirements.txt && cd ../..

# For staffstuddash
cd staffstuddash/backend && pip install -r requirements.txt && cd ../..

# For dropout
cd dropout && pip install sqlalchemy psycopg2-binary python-dotenv && cd ..
```

Done! ✓

---

### **Step 6️⃣ : Verify Connection**

**Run in Terminal/PowerShell:**

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

Done! ✓

---

### **Step 7️⃣ : Start Your Backend**

**Terminal - Window 1:**
```bash
cd Monitoring2.0/backend
python main.py
```

**Terminal - Window 2:**
```bash
cd staffstuddash/backend
python main.py
```

You should see:
```
Application running on 0.0.0.0:8000
Database initialized
```

Done! ✓ **All Set!**

---

## ✅ Success = All These Working

- [ ] NeonDB account created
- [ ] Project created in NeonDB
- [ ] Connection string copied
- [ ] `.env` file has `DATABASE_URL`
- [ ] Dependencies installed (no errors)
- [ ] `verify_database.py` shows all ✓
- [ ] Backends start without errors
- [ ] Can access APIs at `http://localhost:8000`

---

## 🆘 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't connect | Check DATABASE_URL in .env |
| SSL error | Add `?sslmode=require` to URL |
| Timeout | Add `?connect_timeout=10` to URL |
| Dependencies fail | Use Python 3.8+ |
| Still in-memory | Verify DATABASE_URL is set |

---

## 🎯 Key Points

✅ **DATABASE_URL is required** in `.env`
✅ **Must add `?sslmode=require`** at end
✅ **Never commit `.env`** to git
✅ **Free tier available** - Start at $0
✅ **Auto backups** - Data is safe

---

## 📚 More Help

- **Full Guide**: `DATABASE_SETUP.md`
- **Visual Guide**: `NEONDB_VISUAL_GUIDE.md`
- **Quick Ref**: `QUICK_REFERENCE.md`
- **Test Script**: `python verify_database.py`

---

**Total Time: ~15 minutes**

**Result: PostgreSQL connected ✓**

**Status: Production Ready ✓**

🎉 Done!
