from llm_engine import analyze_thinking_quality

# Calculates Learning Momentum Index (LMI)
def calculate_lmi(draft_texts: list) -> float:
    """
    Measures improvement trend across drafts.
    """

    if len(draft_texts) < 2:
        return 20.0  # Not enough data → low learning momentum

    improvements = 0

    # Compare each draft with previous
    for i in range(1, len(draft_texts)):
        if len(draft_texts[i]) > len(draft_texts[i-1]):
            improvements += 1

    # Normalize score to 0–100
    return (improvements / (len(draft_texts)-1)) * 100


# Detects dropout risk
def detect_dropout(integrity: float, lmi: float) -> str:
    """
    Determines dropout category.
    """

    if integrity < 0.3 and lmi < 30:
        return "copy"

    if integrity > 0.4 and lmi < 30:
        return "incapable"

    if integrity < 0.4 and lmi < 50:
        return "no_interest"

    return "safe"


def recalculate_student_stats(student_id: str):
    """
    Re-analyzes student performance based on all assessments.
    Updates the PerformanceRecord in the datastore.
    """
    from datastore import assessments, performance_records
    
    # 1. Filter assessments for this student
    student_logs = [a for a in assessments if a.student_id == student_id]
    
    if not student_logs:
        return # No data to analyse
        
    # 2. Aggregate scores by subject
    subject_totals = {} # { "Math": [90, 95], "History": [60] }
    
    for log in student_logs:
        if log.subject not in subject_totals:
            subject_totals[log.subject] = []
        
        # Normalize to percentage
        pct = (log.score / log.max_score) * 100
        subject_totals[log.subject].append(pct)
        
    # 3. Calculate averages
    averages = {}
    for sub, scores in subject_totals.items():
        averages[sub] = int(sum(scores) / len(scores))
        
    # 4. Determine Strengths (Max) and Weaknesses (Min)
    if not averages:
        new_strengths = []
        new_weaknesses = []
    else:
        max_score = max(averages.values())
        min_score = min(averages.values())
        
        new_strengths = [sub for sub, score in averages.items() if score == max_score]
        
        # Only mark as weakness if it's strictly less than max score
        if min_score < max_score:
            new_weaknesses = [sub for sub, score in averages.items() if score == min_score]
        else:
            new_weaknesses = [] # All scores are equal
    
    # 5. Update the Record
    if student_id in performance_records:
        rec = performance_records[student_id]
        rec["subject_scores"] = averages
        rec["strengths"] = new_strengths
        rec["weaknesses"] = new_weaknesses
        # Simple risk update logic based on average score across all subjects
        total_avg = sum(averages.values()) / len(averages)
        if total_avg < 50:
            rec["dropout_risk"] = "high_risk"
            rec["flagged"] = True
        else:
            rec["dropout_risk"] = "safe"
            rec["flagged"] = False
