from fastapi import APIRouter
from datastore import students, performance_records

router = APIRouter()

@router.get("/dashboard/teacher")
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
            "student_name": student["name"],
            "integrity_score": record["integrity_score"] if record else 1.0,
            "grit_level": record["grit_level"] if record else 0.0,
            "strengths": record["strengths"] if record else [],
            "weaknesses": record["weaknesses"] if record else [],
            "status": record["status"] if record else "unknown",
            "flags": record["flags"] if record else False
        }
        dashboard_data.append(student_summary)
        
    return dashboard_data


@router.get("/dashboard/student/{student_id}")
async def get_student_dashboard(student_id: str):
    """
    Returns data compliant with Instructions 2.0 for the Student Dashboard.
    """
    if student_id not in students:
        return {"error": "Student not found"}
        
    student = students[student_id]
    record = performance_records.get(student_id)
    
    if not record:
        return {"error": "Performance record not found"}
        
    # Construct response based on schema
    return {
        "student_info": {
            "name": student["name"],
            "id": student_id
        },
        "concept_panel": record.get("concept", {}),
        "progress_visuals": record.get("progress", {}),
        "integrity_panel": record.get("integrity", {}),
        "stagnation_tracker": record.get("stagnation", {}),
        # Include raw Integrity Score for sync if needed by frontend separately
        "integrity_score": record.get("integrity", {}).get("integrity_score", 1.0)
    }
