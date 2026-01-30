from services.llm_engine import analyze_thinking_quality

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
        
        # Incorporate integrity into strengths/weaknesses
        integrity = rec.get("integrity_score", 1.0)
        
        if integrity > 0.8:
            if "High Integrity" not in new_strengths:
                new_strengths.append("High Integrity")
        elif integrity < 0.5:
            if "Integrity Concerns" not in new_weaknesses:
                new_weaknesses.append("Integrity Concerns")

        rec["subject_scores"] = averages
        rec["strengths"] = new_strengths
        rec["weaknesses"] = new_weaknesses
        
        # Simple risk update logic based on average score across all subjects
        total_avg = sum(averages.values()) / len(averages)
        if total_avg < 50:
            rec["status"] = "high_risk"
            rec["flags"] = True
        else:
            rec["status"] = "safe"
            rec["flags"] = False

def process_new_draft(student_id: str, draft_text: str):
    """
    Handles a new draft submission:
    1. Stores the draft.
    2. Runs AI Analysis (Groq) against the previous draft.
    3. Updates PerformanceRecord with new integrity/progress insights.
    """
    from datastore import drafts, performance_records
    from models import Draft
    from datetime import datetime
    
    # 1. Store Draft
    if student_id not in drafts:
        drafts[student_id] = []
        
    new_draft = Draft(text=draft_text, timestamp=datetime.now())
    drafts[student_id].append(new_draft)
    
    # 2. AI Analysis
    # We need at least 1 previous draft to compare, or we compare against empty string for the first one
    previous_text = ""
    if len(drafts[student_id]) > 1:
        previous_text = drafts[student_id][-2].text
        
    # Call the Groq-powered engine
    # Returns 0.0 (low thought) to 1.0 (high thought/organic)
    ai_score = analyze_thinking_quality(previous_text, draft_text)
    
    # 3. Update Performance Record
    if student_id not in performance_records:
        return # Should ideally create one, but for now assume student exists
        
    record = performance_records[student_id]
    
    # Update Integrity Panel
    # If AI score is high, integrity is likely consistent (organic thought).
    # If AI score is very low despite big text changes, might be copy-paste (risk).
    
    # Heuristic: 
    # AI Score 0.8-1.0 -> High Integrity
    # AI Score 0.4-0.7 -> Medium
    # AI Score < 0.4 -> Potential Copy/Low Effort
    
    integrity_val = ai_score # Map directly for now for visibility
    
    record["integrity"]["integrity_score"] = integrity_val
    record["integrity_score"] = integrity_val # Legacy field sync
    
    if integrity_val < 0.3:
        record["integrity"]["integrity_status_label"] = "NEEDS_REVIEW"
        record["integrity"]["sudden_jump_flag"] = True
        record["flags"] = True
        record["status"] = "review_needed"
    else:
        record["integrity"]["integrity_status_label"] = "CONSISTENT"
        record["integrity"]["sudden_jump_flag"] = False
        # Do not blindly reset status to safe if they were high risk from grades, 
        # but for this specific flow, let's say they are safe on integrity.
    
    # Update Progress Visuals
    # Semantic change can be proxied by the AI score or just text length diff
    record["progress"]["semantic_change_score"] = ai_score
    
    # Update Reasoning Continuity based on score
    if ai_score > 0.7:
        record["progress"]["reasoning_continuity"] = "HIGH"
    elif ai_score > 0.4:
        record["progress"]["reasoning_continuity"] = "MEDIUM"
    else:
        record["progress"]["reasoning_continuity"] = "LOW"
        
    print(f"Processed draft for {student_id}. AI Score: {ai_score}")

