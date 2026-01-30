env_content = """# NeonDB PostgreSQL Configuration for Veritas Backend
# ==================================================

# DATABASE_URL with NeonDB connection
DATABASE_URL=postgresql://neondb_owner:npg_ewq1EabrNj7T@ep-bitter-night-a1fmjqvj-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# FastAPI Configuration
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Monitoring System Configuration (for Monitoring2.0 backend)
ENABLE_LLM_MONITORING=True
WARNING_THRESHOLD=0.7
CRITICAL_THRESHOLD=0.9

# Groq API Configuration (for AI analysis)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=mixtral-8x7b-32768
GROQ_MAX_TOKENS=1024

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Data Retention (Max logs in database)
MAX_LOG_ENTRIES=10000
"""

with open(r"c:\Users\PRAVEEN RAJA\OneDrive\Desktop\Backend\Veritas\.env", 'w') as f:
    f.write(env_content)

print("[OK] Fixed .env file")
