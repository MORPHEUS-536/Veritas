"""
Integration Examples
Real-world usage scenarios for the Dropout Detection System.
"""

from models import EventType
from main import DropoutDetectionSystem, UserRole
from scoring import ThresholdManager


# ============================================================================
# EXAMPLE 1: JEE/NEET Exam Prep - Student Struggling with Physics
# ============================================================================

def example_1_jee_student():
    """
    Scenario: JEE student struggling with circular motion topic.
    Teacher wants to know if student is dropping out.
    """
    print("=" * 80)
    print("EXAMPLE 1: JEE Student - Physics Circular Motion")
    print("=" * 80)
    print()
    
    system = DropoutDetectionSystem()
    student_id = "JEE_2024_001"
    question_id = "PHYSICS_CIRCULAR_MOTION_Q05"
    question_text = "A ball moves in a vertical circle. Find the minimum speed at top."
    
    # Session 1: First attempt - quick but wrong
    print("📅 Session 1 (Day 1, 2:00 PM):")
    system.record_event(
        EventType.SESSION_START,
        student_id, question_id
    )
    
    system.record_event(
        EventType.QUESTION_START,
        student_id, question_id,
        {"question_content": question_text}
    )
    
    print("  ❌ Attempt 1: Wrong approach (forgot about centripetal force)")
    system.record_event(
        EventType.QUESTION_SUBMIT,
        student_id, question_id,
        {
            "answer": "v = √(gr)",
            "is_correct": False,
            "time_spent_seconds": 120
        }
    )
    
    # Session 2: Second attempt after 6 hours
    print("\n📅 Session 2 (Day 1, 8:00 PM):")
    system.record_event(
        EventType.FOCUS_BLUR,
        student_id, question_id,
        {"idle_duration_seconds": 3600}  # 1 hour idle
    )
    
    system.record_event(
        EventType.QUESTION_START,
        student_id, question_id
    )
    
    print("  ❌ Attempt 2: Partially correct but missing key insight")
    system.record_event(
        EventType.QUESTION_SUBMIT,
        student_id, question_id,
        {
            "answer": "v = √(2gr) - at top only",
            "is_correct": False,
            "time_spent_seconds": 180
        }
    )
    
    # Session 3: Third attempt next day
    print("\n📅 Session 3 (Day 2, 10:00 AM):")
    system.record_event(
        EventType.QUESTION_START,
        student_id, question_id
    )
    
    print("  ❌ Attempt 3: Rushed answer, not thinking deeply")
    system.record_event(
        EventType.QUESTION_SUBMIT,
        student_id, question_id,
        {
            "answer": "v = √(5gr)",
            "is_correct": False,
            "time_spent_seconds": 90  # Rushing
        }
    )
    
    print("\n🔍 Analyzing Student Progress...")
    print()
    
    # Teacher view
    teacher_report = system.analyze(
        student_id, question_id,
        question_context=question_text,
        role=UserRole.TEACHER
    )
    
    print("👨‍🏫 TEACHER ANALYSIS:")
    print("-" * 80)
    status = teacher_report['dropout_status']
    print(f"Status: {status['status']}")
    print(f"Confidence: {status['confidence']}")
    print()
    
    if status['status'] == "DROPOUT_DETECTED":
        print(f"Dropout Types: {', '.join(status['types'])}")
        print(f"Primary Issue: {status['reason']}")
        print()
    
    print(f"Metrics:")
    print(f"  - Learning Momentum (LMI): {teacher_report['scores']['lmi']['score']:.1f}/100")
    print(f"  - Dropout Risk (DRS): {teacher_report['scores']['drs']['score']:.2f}/1.0")
    print(f"  - Risk Level: {teacher_report['scores']['drs']['level']}")
    print()
    
    print(f"Recommendation:")
    print(f"  {teacher_report['intervention']['recommendation']}")
    print()
    
    # Student view
    student_report = system.analyze(
        student_id, question_id,
        question_context=question_text,
        role=UserRole.STUDENT
    )
    
    print("👨‍🎓 STUDENT FEEDBACK:")
    print("-" * 80)
    
    if student_report["strengths"]:
        print("💪 What you're doing well:")
        for strength in student_report["strengths"]:
            print(f"  ✓ {strength}")
        print()
    
    if student_report["growth_areas"]:
        print("📚 Let's focus on:")
        for area in student_report["growth_areas"]:
            print(f"  • {area['area']}")
            print(f"    → {area['message']}")
        print()
    
    print(f"💡 Next Step: {student_report['difficulty_suggestion']}")
    print()


# ============================================================================
# EXAMPLE 2: Online Course - Engagement Dropout Detection
# ============================================================================

def example_2_online_course():
    """
    Scenario: Online course platform detecting engagement dropout.
    Multiple students' progress on a coding assignment.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Online Course - Engagement Dropout Detection")
    print("=" * 80)
    print()
    
    system = DropoutDetectionSystem()
    
    students = [
        ("COURSE_STUDENT_A", "CODING_ASSIGN_1", "Write a Python function to find prime numbers"),
        ("COURSE_STUDENT_B", "CODING_ASSIGN_1", "Write a Python function to find prime numbers"),
    ]
    
    # Student A: Healthy progression
    print("📊 Analyzing Course Progress...")
    print()
    
    print("Student A - Consistent Engagement:")
    print("-" * 40)
    
    student_a_id, question_a_id, context_a = students[0]
    
    # Multiple attempts with learning
    for i in range(1, 4):
        system.record_event(
            EventType.QUESTION_SUBMIT,
            student_a_id, question_a_id,
            {
                "answer": f"def find_primes(n): # attempt {i}",
                "is_correct": (i == 3),
                "time_spent_seconds": 300 - (i * 50)
            }
        )
        print(f"  Attempt {i}: {'✓ Correct' if i == 3 else '✗ Learning'}")
    
    student_a_report = system.analyze(
        student_a_id, question_a_id,
        question_context=context_a,
        role=UserRole.TEACHER
    )
    
    print(f"Result: {student_a_report['dropout_status']['status']}")
    print(f"LMI: {student_a_report['scores']['lmi']['score']:.1f}/100")
    print()
    
    # Student B: Disengaging
    print("Student B - Disengaging:")
    print("-" * 40)
    
    student_b_id, question_b_id, context_b = students[1]
    
    # Multiple attempts, getting worse
    for i in range(1, 4):
        system.record_event(
            EventType.QUESTION_SUBMIT,
            student_b_id, question_b_id,
            {
                "answer": "pass",  # Minimal effort
                "is_correct": False,
                "time_spent_seconds": 100  # Less time each attempt
            }
        )
        print(f"  Attempt {i}: ✗ Minimal effort")
    
    student_b_report = system.analyze(
        student_b_id, question_b_id,
        question_context=context_b,
        role=UserRole.TEACHER
    )
    
    print(f"Result: {student_b_report['dropout_status']['status']}")
    print(f"LMI: {student_b_report['scores']['lmi']['score']:.1f}/100")
    
    if student_b_report['dropout_status']['status'] == "DROPOUT_DETECTED":
        print(f"Types: {', '.join(student_b_report['dropout_status']['types'])}")
        print()
        print("⚠️ ALERT: This student needs intervention!")
        print(f"Action: {student_b_report['intervention']['recommendation']}")
    print()


# ============================================================================
# EXAMPLE 3: Competitive Exam Mock Tests - Rank-Based Pressure
# ============================================================================

def example_3_mock_rank_pressure():
    """
    Scenario: Student's performance declining after mock test rank drop.
    Demonstrates competition-aware signal detection.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Competition Pressure - Mock Test Rank Decline")
    print("=" * 80)
    print()
    
    system = DropoutDetectionSystem()
    student_id = "COMPETITIVE_001"
    question_id = "Q_AFTER_MOCK_01"
    
    print("📋 Scenario:")
    print("  - Mock Test 5: Rank 250 → Rank 500 (dropped 250 positions)")
    print("  - Student now solving questions from the test")
    print()
    
    # Record events with rank context
    print("📝 Student's Recent Attempts:")
    
    for i in range(1, 4):
        system.record_event(
            EventType.QUESTION_SUBMIT,
            student_id, question_id,
            {
                "answer": f"attempt_{i}",
                "is_correct": False,
                "time_spent_seconds": 150 + (i * 100)  # Getting slower
            }
        )
        print(f"  Attempt {i}: ✗ Incorrect, {150 + (i*100)}s spent")
    
    # Analyze with rank information
    report = system.analyze(
        student_id, question_id,
        role=UserRole.TEACHER
    )
    
    print()
    print("🔍 Analysis with Competition Awareness:")
    print("-" * 80)
    
    competition_signals = report['signals']['5_competition_aware']
    print(f"Latest Mock Rank: {competition_signals['latest_mock_rank']}")
    print(f"Previous Mock Rank: {competition_signals['previous_mock_rank']}")
    print(f"Rank Delta: {competition_signals['rank_delta']}")
    print(f"Competition Pressure: {competition_signals['competition_pressure_flag']}")
    print()
    
    if report['dropout_status']['status'] == "DROPOUT_DETECTED":
        factors = report['risk_factors']
        if "Competition pressure" in str(factors):
            print("⚠️ Competition pressure is a key dropout risk factor!")
            print()
            print("💡 Teacher Action Plan:")
            print("  1. Acknowledge the setback - it's temporary")
            print("  2. Focus on learning, not ranking")
            print("  3. Break problems into smaller goals")
            print("  4. Celebrate small wins")
    print()


# ============================================================================
# EXAMPLE 4: Silent Dropout Detection
# ============================================================================

def example_4_silent_dropout():
    """
    Scenario: Student appears to be working but learning isn't happening.
    This is the most dangerous form of dropout.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Silent Dropout - The Most Dangerous Form")
    print("=" * 80)
    print()
    
    system = DropoutDetectionSystem()
    student_id = "SILENT_DROPOUT_001"
    question_id = "MATH_CALCULUS_Q03"
    
    print("📋 Scenario:")
    print("  - Student logged in every day")
    print("  - Submitted answers on time")
    print("  - No obvious behavioral issues")
    print("  - BUT: Making the same mistakes repeatedly")
    print()
    
    print("📝 Student Activity Log:")
    print()
    
    # Attempt 1-5: Same mistake each time
    for i in range(1, 6):
        system.record_event(
            EventType.QUESTION_SUBMIT,
            student_id, question_id,
            {
                "answer": "d/dx(x²) = 2x (forgot the derivative of base)",  # Same mistake
                "is_correct": False,
                "time_spent_seconds": 180  # Consistent time (seems engaged)
            }
        )
        print(f"  Day {i}: Submitted answer - {180}s spent - ✗ Wrong (same mistake)")
    
    print()
    print("🔍 Analysis:")
    print("-" * 80)
    
    report = system.analyze(student_id, question_id, role=UserRole.TEACHER)
    
    status = report['dropout_status']
    print(f"Dropout Status: {status['status']}")
    
    if status['status'] == "DROPOUT_DETECTED":
        print(f"Types Detected: {', '.join(status['types'])}")
        print()
        print("🚨 CRITICAL INSIGHT:")
        if "SILENT" in str(status['types']):
            print("  This is SILENT DROPOUT - the most dangerous kind!")
            print()
            print("  Why it's dangerous:")
            print("    - Student appears engaged (submits answers)")
            print("    - System shows activity")
            print("    - But learning has stopped")
            print("    - Student doesn't realize they're stuck")
            print()
            print("  What to do:")
            print("    1. Immediate one-on-one check-in")
            print("    2. Review fundamental concepts together")
            print("    3. Identify specific misconception")
            print("    4. Rebuild confidence")
    print()


# ============================================================================
# EXAMPLE 5: Batch Analysis of Multiple Students
# ============================================================================

def example_5_batch_analysis():
    """
    Scenario: Teacher analyzing a whole class for dropout risks.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Batch Class Analysis - Identify At-Risk Students")
    print("=" * 80)
    print()
    
    system = DropoutDetectionSystem()
    
    # Create multiple student scenarios
    scenarios = [
        ("STU_A", "Q_01", "Healthy", lambda: [(120, True), (100, True), (80, True)]),
        ("STU_B", "Q_01", "Cognitive", lambda: [(120, False), (150, False), (200, False)]),
        ("STU_C", "Q_01", "Engagement", lambda: [(120, False), (200, False), (300, False)]),
        ("STU_D", "Q_01", "Silent", lambda: [(120, False), (120, False), (120, False)]),
    ]
    
    results = []
    
    print("📊 Analyzing Class of 4 Students...")
    print()
    
    for student_id, question_id, scenario_type, attempt_gen in scenarios:
        # Generate attempts
        for time_spent, is_correct in attempt_gen():
            system.record_event(
                EventType.QUESTION_SUBMIT,
                student_id, question_id,
                {
                    "answer": f"answer_attempt",
                    "is_correct": is_correct,
                    "time_spent_seconds": time_spent
                }
            )
        
        # Analyze
        report = system.analyze(student_id, question_id, role=UserRole.TEACHER)
        
        results.append({
            "student_id": student_id,
            "scenario": scenario_type,
            "is_dropout": report['dropout_status']['status'] == "DROPOUT_DETECTED",
            "lmi": report['scores']['lmi']['score'],
            "drs": report['scores']['drs']['score'],
            "risk_level": report['scores']['drs']['level']
        })
    
    # Display results
    print("Class Report:")
    print("-" * 80)
    print(f"{'Student':<10} {'Scenario':<15} {'Status':<15} {'LMI':<8} {'DRS':<8} {'Risk':<10}")
    print("-" * 80)
    
    for r in results:
        status = "DROPOUT" if r['is_dropout'] else "OK"
        print(f"{r['student_id']:<10} {r['scenario']:<15} {status:<15} {r['lmi']:<8.1f} {r['drs']:<8.2f} {r['risk_level']:<10}")
    
    print()
    print("📋 Action Items:")
    print("-" * 80)
    
    for r in results:
        if r['is_dropout']:
            print(f"  ⚠️ {r['student_id']}: {r['scenario']} dropout detected - needs intervention")
    
    print()


# ============================================================================
# RUN ALL EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("=" * 80)
    print("  DROPOUT DETECTION SYSTEM - INTEGRATION EXAMPLES  ".center(80))
    print("=" * 80)
    print("\n")
    
    # Run all examples
    example_1_jee_student()
    example_2_online_course()
    example_3_mock_rank_pressure()
    example_4_silent_dropout()
    example_5_batch_analysis()
    
    print("\n" + "=" * 80)
    print("  OK - ALL EXAMPLES COMPLETE  ".center(80))
    print("=" * 80)
    print("\n")
