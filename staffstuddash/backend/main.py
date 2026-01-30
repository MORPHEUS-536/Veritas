import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import students, assessments, dashboard, general
from datastore import datastore

# Load environment variables from .env file in parent directory
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=str(env_path))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    logger.info("Starting Evolve AI Backend...")
    logger.info(f"Database connection status: {'Fallback (in-memory)' if datastore.use_fallback else 'PostgreSQL via NeonDB'}")
    yield
    logger.info("Shutting down Evolve AI Backend...")


app = FastAPI(
    title="Evolve AI Backend",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(general.router)
app.include_router(students.router)
app.include_router(assessments.router)
app.include_router(dashboard.router)
