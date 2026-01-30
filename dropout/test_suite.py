"""
Configuration and Testing Module
Contains default settings and comprehensive test cases.
"""

from enum import Enum
from models import EventType
from main import DropoutDetectionSystem, UserRole
from datetime import datetime, timedelta


class TestScenario(Enum):
    """Predefined test scenarios."""
    HEALTHY_LEARNER = "healthy"
    COGNITIVE_DROPOUT = "cognitive"
    BEHAVIORAL_DROPOUT = "behavioral"
    ENGAGEMENT_DROPOUT = "engagement"
    SILENT_DROPOUT = "silent"


class DropoutTestSuite:
    """
    Comprehensive test suite for the Dropout Detection System.
    Tests various dropout scenarios.
    """
    
    def __init__(self):
        self.system = DropoutDetectionSystem()
        self.test_results = []
    
    def run_all_tests(self):
        """Run all test scenarios."""
        print("=" * 80)
        print("DROPOUT DETECTION SYSTEM - TEST SUITE")
        print("=" * 80)
        print()
        
        scenarios = [
            ("Healthy Learner", self.test_healthy_learner),
            ("Cognitive Dropout", self.test_cognitive_dropout),
            ("Behavioral Dropout", self.test_behavioral_dropout),
            ("Engagement Dropout", self.test_engagement_dropout),
            ("Silent Dropout", self.test_silent_dropout),
        ]
        
        for name, test_func in scenarios:
            print(f"\n{'='*80}")
            print(f"TEST: {name}")
            print('='*80)
            try:
                test_func()
                self.test_results.append((name, "PASSED"))
            except AssertionError as e:
                print(f"❌ TEST FAILED: {e}")
                self.test_results.append((name, "FAILED"))
            except Exception as e:
                print(f"❌ ERROR: {e}")
                self.test_results.append((name, "ERROR"))
        
        self._print_summary()
    
    def test_healthy_learner(self):
        """Test case: Student with healthy learning progression."""
        student_id = "STU_HEALTHY"
        question_id = "Q001"
        
        # First attempt: Correct immediately
        self.system.record_event(
            EventType.QUESTION_START,
            student_id, question_id,
            {"question_content": "What is 2+2?"}
        )
        
        self.system.record_event(
            EventType.QUESTION_SUBMIT,
            student_id, question_id,
            {"answer": "4", "is_correct": True, "time_spent_seconds": 45}
        )
        
        # Analyze
        report = self.system.analyze(student_id, question_id, role=UserRole.TEACHER)
        
        print(f"Status: {report['dropout_status']['status']}")
        print(f"Confidence: {report['dropout_status']['confidence']}")
        
        assert report['dropout_status']['status'] == "NO_DROPOUT", "Healthy learner incorrectly classified as dropout"
        assert float(report['scores']['lmi']['score']) > 70, "LMI should be > 70 for healthy learner"
        assert float(report['scores']['drs']['score']) < 0.3, "DRS should be < 0.3 for healthy learner"
        
        print("✓ Healthy learner correctly identified")
    
    def test_cognitive_dropout(self):
        """Test case: Student with declining conceptual understanding."""
        student_id = "STU_COGNITIVE"
        question_id = "Q002"
        
        # Multiple attempts with wrong answers (no learning)
        for i in range(4):
            self.system.record_event(
                EventType.QUESTION_START,
                student_id, question_id
            )
            
            self.system.record_event(
                EventType.QUESTION_SUBMIT,
                student_id, question_id,
                {
                    "answer": f"wrong_answer_{i}",
                    "is_correct": False,
                    "time_spent_seconds": 120 + (i * 30)
                }
            )
        
        # Analyze
        report = self.system.analyze(student_id, question_id, role=UserRole.TEACHER)
        
        print(f"Status: {report['dropout_status']['status']}")
        print(f"LMI: {report['scores']['lmi']['score']:.1f}")
        print(f"DRS: {report['scores']['drs']['score']:.2f}")
        
        # Should show signs of cognitive issues
        lmi = float(report['scores']['lmi']['score'])
        drs = float(report['scores']['drs']['score'])
        
        assert lmi < 50, "LMI should be low for cognitive dropout"
        print("✓ Cognitive dropout pattern detected")
    
    def test_behavioral_dropout(self):
        """Test case: Student with erratic behavior and inconsistency."""
        student_id = "STU_BEHAVIORAL"
        question_id = "Q003"
        
        # Erratic attempt pattern
        time_gaps = [30, 60, 300, 45, 600]  # Large gap in middle
        
        for i, gap in enumerate(time_gaps):
            self.system.record_event(
                EventType.QUESTION_START,
                student_id, question_id
            )
            
            self.system.record_event(
                EventType.QUESTION_SUBMIT,
                student_id, question_id,
                {
                    "answer": "answer",
                    "is_correct": i % 2 == 0,
                    "time_spent_seconds": gap
                }
            )
        
        # Analyze
        report = self.system.analyze(student_id, question_id, role=UserRole.TEACHER)
        
        print(f"Status: {report['dropout_status']['status']}")
        print(f"Behavioral Consistency: {report['signals']['6_behavioral_disengagement']['consistency_score']}")
        
        consistency_str = report['signals']['6_behavioral_disengagement']['consistency_score']
        consistency = float(str(consistency_str).replace('%', '')) if '%' in str(consistency_str) else float(consistency_str)
        assert consistency < 70, "Consistency should be low for behavioral dropout"
        
        print("✓ Behavioral dropout pattern detected")
    
    def test_engagement_dropout(self):
        """Test case: Student with declining effort/engagement."""
        student_id = "STU_ENGAGEMENT"
        question_id = "Q004"
        
        # Multiple attempts with declining quality
        for i in range(3):
            self.system.record_event(
                EventType.QUESTION_START,
                student_id, question_id
            )
            
            # Time spent decreases (rushing)
            time_spent = 300 - (i * 80)
            
            # Answer length decreases (less effort)
            answer_length = 100 - (i * 30)
            answer = "x" * max(10, answer_length)
            
            self.system.record_event(
                EventType.QUESTION_SUBMIT,
                student_id, question_id,
                {
                    "answer": answer,
                    "is_correct": False,
                    "time_spent_seconds": time_spent
                }
            )
        
        # Analyze
        report = self.system.analyze(student_id, question_id, role=UserRole.TEACHER)
        
        print(f"Status: {report['dropout_status']['status']}")
        print(f"Average gap increasing: {report['signals']['6_behavioral_disengagement']['average_gap_increasing']}")
        
        print("✓ Engagement dropout pattern detected")
    
    def test_silent_dropout(self):
        """Test case: Student appears active but learning momentum collapsing."""
        student_id = "STU_SILENT"
        question_id = "Q005"
        
        # Appears active: many attempts, consistent timing
        # But: no learning, answers are superficial variations
        for i in range(5):
            self.system.record_event(
                EventType.QUESTION_START,
                student_id, question_id
            )
            
            # Similar answer each time (superficial change)
            answer = "answer_" + ("a" * i)  # Minimal variation
            
            self.system.record_event(
                EventType.QUESTION_SUBMIT,
                student_id, question_id,
                {
                    "answer": answer,
                    "is_correct": False,
                    "time_spent_seconds": 180  # Consistent timing (appears engaged)
                }
            )
        
        # Analyze
        report = self.system.analyze(student_id, question_id, role=UserRole.TEACHER)
        
        print(f"Status: {report['dropout_status']['status']}")
        print(f"Semantic change score: {report['signals']['1_learning_progress']['semantic_change_score']}")
        print(f"Attempt count: {report['signals']['1_learning_progress']['attempt_count']}")
        
        semantic_str = report['signals']['1_learning_progress']['semantic_change_score']
        semantic_change = float(str(semantic_str).replace('%', '')) if '%' in str(semantic_str) else float(semantic_str)
        assert semantic_change < 30, "Silent dropout has low semantic change"
        
        print("✓ Silent dropout pattern detected")
    
    def _print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for _, result in self.test_results if result == "PASSED")
        total = len(self.test_results)
        
        for test_name, result in self.test_results:
            icon = "✓" if result == "PASSED" else "✗"
            print(f"{icon} {test_name}: {result}")
        
        print()
        print(f"Results: {passed}/{total} tests passed")


class PerformanceBenchmark:
    """Benchmark system performance."""
    
    @staticmethod
    def benchmark_analysis_speed():
        """Benchmark time for complete analysis."""
        import time
        
        system = DropoutDetectionSystem()
        student_id = "STU_BENCH"
        question_id = "Q_BENCH"
        
        # Record multiple events
        for i in range(10):
            system.record_event(
                EventType.QUESTION_SUBMIT,
                student_id, question_id,
                {
                    "answer": f"answer_{i}",
                    "is_correct": i % 2 == 0,
                    "time_spent_seconds": 100 + i * 10
                }
            )
        
        # Time the analysis
        start = time.time()
        report = system.analyze(student_id, question_id, role=UserRole.TEACHER)
        elapsed = time.time() - start
        
        print("=" * 80)
        print("PERFORMANCE BENCHMARK")
        print("=" * 80)
        print(f"Analysis of 10 attempts: {elapsed*1000:.2f}ms")
        print()


def demonstrate_teacher_student_views():
    """Demonstrate both teacher and student views."""
    print("=" * 80)
    print("TEACHER VS STUDENT VIEW DEMONSTRATION")
    print("=" * 80)
    print()
    
    system = DropoutDetectionSystem()
    student_id = "STU_DEMO"
    question_id = "Q_DEMO"
    
    # Simulate a struggling student
    print("📝 Simulating student struggling with a question...")
    print()
    
    # Attempt 1: Wrong
    system.record_event(EventType.QUESTION_START, student_id, question_id)
    system.record_event(
        EventType.QUESTION_SUBMIT, student_id, question_id,
        {"answer": "Wrong approach", "is_correct": False, "time_spent_seconds": 180}
    )
    
    # Attempt 2: Still wrong
    system.record_event(EventType.QUESTION_START, student_id, question_id)
    system.record_event(
        EventType.QUESTION_SUBMIT, student_id, question_id,
        {"answer": "Still wrong", "is_correct": False, "time_spent_seconds": 240}
    )
    
    # Attempt 3: Slightly better but still wrong
    system.record_event(EventType.QUESTION_START, student_id, question_id)
    system.record_event(
        EventType.QUESTION_SUBMIT, student_id, question_id,
        {"answer": "Getting closer", "is_correct": False, "time_spent_seconds": 200}
    )
    
    print("👨‍🏫 TEACHER VIEW:")
    print("-" * 80)
    teacher_report = system.analyze(student_id, question_id, role=UserRole.TEACHER)
    
    dropout_status = teacher_report['dropout_status']
    print(f"Dropout Status: {dropout_status['status']}")
    print(f"LMI: {teacher_report['scores']['lmi']['score']:.1f}/100")
    print(f"DRS: {teacher_report['scores']['drs']['score']:.2f}/1.0")
    print(f"Risk Factors: {', '.join(teacher_report['risk_factors'][:2])}")
    print()
    
    print("👨‍🎓 STUDENT VIEW:")
    print("-" * 80)
    student_report = system.analyze(student_id, question_id, role=UserRole.STUDENT)
    
    print("💪 Strengths:")
    for strength in student_report['strengths']:
        print(f"  ✓ {strength}")
    print()
    
    print("📈 Next Steps:")
    print(f"  → {student_report['difficulty_suggestion']}")
    print()
    
    print("💡 Encouragement:")
    encouragement = student_report['encouragement']
    print(f'  "{encouragement}"')
    print()


# Configuration constants
class Config:
    """System configuration."""
    
    # LMI Thresholds
    LMI_HEALTHY_THRESHOLD = 70
    LMI_AT_RISK_THRESHOLD = 40
    
    # DRS Thresholds
    DRS_LOW_THRESHOLD = 0.3
    DRS_MEDIUM_THRESHOLD = 0.6
    DRS_HIGH_THRESHOLD = 0.8
    
    # Stagnation Thresholds
    STAGNATION_DURATION_MINUTES = 15
    STAGNATION_MIN_ATTEMPTS = 3
    
    # Semantic Change Threshold
    SEMANTIC_CHANGE_MIN_THRESHOLD = 30
    
    # Intervention Thresholds
    INTERVENTION_DRS_THRESHOLD = 0.6
    INTERVENTION_LMI_THRESHOLD = 40


if __name__ == "__main__":
    # Run all demonstrations
    
    # 1. Run comprehensive test suite
    test_suite = DropoutTestSuite()
    test_suite.run_all_tests()
    
    # 2. Run performance benchmark
    print("\n")
    PerformanceBenchmark.benchmark_analysis_speed()
    
    # 3. Demonstrate teacher vs student views
    print("\n")
    demonstrate_teacher_student_views()
    
    print("\n" + "=" * 80)
    print("✓ ALL DEMONSTRATIONS COMPLETE")
    print("=" * 80)
