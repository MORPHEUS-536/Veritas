from fastapi import APIRouter
from models import AssessmentLog
from datastore import assessments
from services.scoring import recalculate_student_stats

router = APIRouter()

@router.post("/assessments")
async def add_assessment(assessment: AssessmentLog):
    """
    Receives a new assessment log (test/hw score).
    Saves it to datastore and recalculates analytics for the student.
    """
    
    # 1. Save the raw log
    assessments.append(assessment)
    
    # 2. Trigger analysis update
    recalculate_student_stats(assessment.student_id)
    
    return {"status": "recorded", "current_count": len(assessments)}
