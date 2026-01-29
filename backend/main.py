from fastapi import FastAPI
from datetime import datetime

from models import Student, Draft, PerformanceRecord, AssessmentLog
from datastore import students, drafts, performance_records
from llm_engine import analyze_thinking_quality
from scoring import calculate_lmi, detect_dropout
from monitoring import check_if_stuck


app = FastAPI(title="Evolve AI Backend")


@app.get("/")
async def root():
    return {"message": "Evolve AI Backend API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/students")
async def get_students():
    return students


@app.post("/students")
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
        "lmi_score": 0.0,
        "dropout_risk": "safe",
        "flagged": False,
        "recap_required": False
    }
    
    return {"status": "created", "student": student}

@app.delete("/students/{student_id}")
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


@app.get("/drafts")
async def get_drafts():
    return drafts


@app.get("/performance-records")
async def get_performance_records():
    return performance_records


@app.get("/dashboard/teacher")
async def get_teacher_dashboard():
    """
    Returns aggregated data for the teacher's dashboard.
    Effectively joins 'Students' with their 'PerformanceRecords'.
    """
    dashboard_data = []
    
    # Iterate through all students in our datastore
    for s_id, student in students.items():
        # Retrieve the matching performance record, if any
        record = performance_records.get(s_id)
        
        # Build the student summary object
        student_summary = {
            "student_id": s_id,
            "name": student["name"],
            # Default to empty lists/dicts if no record exists yet
            "strengths": record["strengths"] if record else [],
            "weaknesses": record["weaknesses"] if record else [],
            "scores": record["subject_scores"] if record else {},
            "risk_level": record["dropout_risk"] if record else "unknown",
            "flagged": record["flagged"] if record else False
        }
        dashboard_data.append(student_summary)
        
    return dashboard_data


@app.post("/assessments")
async def add_assessment(assessment: AssessmentLog):
    """
    Receives a new assessment log (test/hw score).
    Saves it to datastore and recalculates analytics for the student.
    """
    from datastore import assessments
    from scoring import recalculate_student_stats
    
    # 1. Save the raw log
    assessments.append(assessment)
    
    # 2. Trigger analysis update
    recalculate_student_stats(assessment.student_id)
    
    return {"status": "recorded", "current_count": len(assessments)}
