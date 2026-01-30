from fastapi import APIRouter
from models import Student
from datastore import students, performance_records

router = APIRouter()

@router.get("/students")
async def get_students():
    return students


@router.post("/students")
async def create_student(student: Student):
    """
    Registers a new student manually.
    """
    if student.id in students:
        return {"error": "Student already exists"}
    
    # Store as dict (or object depending on usage, matching existing pattern)
    students[student.id] = student.dict()
    
    # Initialize empty performance record
    performance_records[student.id] = {
        "student_id": student.id,
        "strengths": [],
        "weaknesses": [],
        "subject_scores": {},
        "integrity_score": 1.0, # Default start
        "grit_level": 0.0,
        "status": "safe",
        "flags": False,
        "recap_required": False,
        "concept": {
            "concept_id": "intro_math_101",
            "concept_name": "Basic Algebra",
            "subject": "Math",
            "difficulty_level": 1,
            "attempt_count": 0
        },
        "progress": {
            "learning_progress_score": 0.0,
            "semantic_change_score": 0.0,
            "reasoning_continuity": "MEDIUM"
        },
        "integrity": {
            "integrity_score": 1.0,
            "sudden_jump_flag": False,
            "integrity_status_label": "CONSISTENT"
        },
        "stagnation": {
            "stagnation_duration_minutes": 0.0,
            "repeat_attempt_count": 0,
            "no_progress_flag": False,
            "learning_state": "PROGRESSING",
            "dropout_risk_level": "LOW"
        }
    }
    
    return {"status": "created", "student": student}

@router.post("/students/{student_id}/drafts")
async def submit_draft(student_id: str, draft: dict):
    """
    Submits a new draft for analysis.
    Body: {"text": "..."}
    """
    from services.scoring import process_new_draft
    
    if student_id not in students:
        return {"error": "Student not found"}
        
    text = draft.get("text", "")
    process_new_draft(student_id, text)
    
    return {"status": "analyzed", "student_id": student_id}


@router.delete("/students/{student_id}")
async def delete_student(student_id: str):
    """
    Deletes a student and all their associated data.
    """
    from datastore import assessments
    
    if student_id not in students:
        return {"error": "Student not found"}
        
    # 1. Remove from students registry
    del students[student_id]
    
    # 2. Remove performance record
    if student_id in performance_records:
        del performance_records[student_id]
        
    # 3. Remove assessments (filter them out)
    assessments[:] = [a for a in assessments if a.student_id != student_id]
    
    return {"status": "deleted", "student_id": student_id}
