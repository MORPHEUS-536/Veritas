from fastapi import APIRouter
from datastore import drafts, performance_records

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Evolve AI Backend API is running"}


@router.get("/health")
async def health_check():
    return {"status": "healthy"}


@router.get("/drafts")
async def get_drafts():
    return drafts


@router.get("/performance-records")
async def get_performance_records():
    return performance_records


