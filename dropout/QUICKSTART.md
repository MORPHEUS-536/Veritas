# QUICK START GUIDE - Dropout Detection System

## 🚀 30-Second Start

```bash
# Run the main demo
python main.py

# Run comprehensive tests
python test_suite.py

# Run real-world examples
python examples.py
```

## 📝 5-Minute Integration

```python
from main import DropoutDetectionSystem, UserRole
from models import EventType

# Create system
system = DropoutDetectionSystem()

# Record student attempts
system.record_event(
    EventType.QUESTION_SUBMIT,
    student_id="STU001",
    question_id="Q001",
    data={
        "answer": "x = 4",
        "is_correct": True,
        "time_spent_seconds": 120
    }
)

# Get analysis for teacher
teacher_report = system.analyze(
    "STU001", "Q001",
    question_context="Solve: 2x + 5 = 13",
    role=UserRole.TEACHER
)

print(teacher_report['dropout_status']['status'])  # NO_DROPOUT or DROPOUT_DETECTED
print(f"LMI: {teacher_report['scores']['lmi']['score']:.1f}/100")
print(f"DRS: {teacher_report['scores']['drs']['score']:.2f}/1.0")

# Get student-friendly feedback
student_report = system.analyze(
    "STU001", "Q001",
    role=UserRole.STUDENT
)

print(student_report['encouragement'])
```

## 📊 Understanding the Output

### Teacher Report Keys
- `dropout_status['status']` → "NO_DROPOUT" or "DROPOUT_DETECTED"
- `dropout_status['types']` → List of dropout types if detected
- `scores['lmi']['score']` → Learning Momentum (0-100)
  - > 70 = Healthy
  - 40-70 = At-risk
  - < 40 = Critical
- `scores['drs']['score']` → Dropout Risk (0-1)
  - 0-0.3 = Low
  - 0.3-0.6 = Medium
  - 0.6-0.8 = High
  - 0.8-1.0 = Critical
- `intervention['recommendation']` → What to do

### Student Report Keys
- `strengths` → Positive feedback
- `growth_areas` → Constructive areas to focus on
- `encouragement` → Motivational message
- `difficulty_suggestion` → Next recommended action

## 🎯 Common Scenarios

### Scenario 1: Check if Student is Dropping Out
```python
# After student has attempted same problem 3+ times without success
system.record_event(EventType.QUESTION_SUBMIT, student_id, q_id, {...})
system.record_event(EventType.QUESTION_SUBMIT, student_id, q_id, {...})
system.record_event(EventType.QUESTION_SUBMIT, student_id, q_id, {...})

report = system.analyze(student_id, q_id, role=UserRole.TEACHER)

if report['dropout_status']['status'] == "DROPOUT_DETECTED":
    print(f"Student needs help! {report['intervention']['recommendation']}")
```

### Scenario 2: Monitor Class Progress
```python
for student_id in class_student_ids:
    report = system.analyze(student_id, question_id, role=UserRole.TEACHER)
    
    if report['scores']['drs']['level'] in ['HIGH', 'CRITICAL']:
        print(f"Alert: {student_id} - {report['intervention']['recommendation']}")
```

### Scenario 3: Check for Silent Dropout
```python
# Student appears active but learning isn't happening
# System will detect if LMI is low while behavior seems normal

report = system.analyze(student_id, q_id, role=UserRole.TEACHER)

if "SILENT" in str(report['dropout_status']['types']):
    print("Silent dropout detected! This needs immediate attention.")
```

## 📚 File Guide

| File | Purpose | Lines |
|------|---------|-------|
| `models.py` | Data structures and enums | 300+ |
| `event_collector.py` | Layer 1: Event collection | 250+ |
| `feature_extractor.py` | Layer 2: Feature extraction | 400+ |
| `llm_analyzer.py` | Layer 3: LLM analysis | 300+ |
| `scoring.py` | Layer 4: Scoring (LMI & DRS) | 400+ |
| `dropout_classifier.py` | Layer 5: Classification | 350+ |
| `main.py` | Layer 6: Orchestrator & views | 700+ |
| `test_suite.py` | Comprehensive tests | 400+ |
| `examples.py` | Real-world examples | 500+ |
| `README.md` | Full documentation | 800+ |
| `SYSTEM_SUMMARY.md` | Project summary | 300+ |

## 🔧 Configuration

All thresholds are in `test_suite.py` under `Config` class:

```python
class Config:
    LMI_HEALTHY_THRESHOLD = 70        # LMI above this = healthy
    LMI_AT_RISK_THRESHOLD = 40        # Below this = critical
    DRS_MEDIUM_THRESHOLD = 0.6        # DRS above this = intervention needed
    STAGNATION_DURATION_MINUTES = 15  # Stuck for 15+ min = stalled
    SEMANTIC_CHANGE_MIN_THRESHOLD = 30 # Learning must show 30%+ change
```

## 🎓 The 7 Signal Categories

1. **Learning Progress** - Is student moving forward?
2. **Stagnation** - Is student stuck?
3. **Integrity** - Is learning authentic?
4. **AI Reasoning** - Why is student struggling?
5. **Competition** - Is rank pressure causing dropout?
6. **Behavioral** - Is effort declining?
7. **Intervention Response** - Did help work?

## ⚡ Quick Tips

### Tip 1: Record Rich Data
More detailed event data → Better analysis
```python
# Good
system.record_event(EventType.QUESTION_SUBMIT, student_id, q_id, {
    "answer": "detailed_answer_text",
    "is_correct": True,
    "time_spent_seconds": 145
})

# Less useful
system.record_event(EventType.QUESTION_SUBMIT, student_id, q_id, {})
```

### Tip 2: Analyze Frequently
More frequent analysis → Earlier detection
```python
# Analyze after every 3 attempts
if attempt_count % 3 == 0:
    report = system.analyze(student_id, q_id, role=UserRole.TEACHER)
```

### Tip 3: Never Show Dropout Label to Student
Student view automatically hides harsh language
```python
# Teacher sees this
print(report['dropout_status']['status'])  # "DROPOUT_DETECTED"

# Student sees this
print(student_report['encouragement'])  # "Your persistence is impressive!"
```

### Tip 4: Use Confidence Scores
Lower confidence → Monitor instead of intervene
```python
confidence = report['dropout_status']['confidence']
if confidence > 0.7 and report['dropout_status']['status'] == "DROPOUT_DETECTED":
    # High confidence dropout - take action
else:
    # Low confidence - monitor but don't panic
```

### Tip 5: Check Risk Factors
Understand what caused the dropout flag
```python
risk_factors = report['risk_factors']
print(f"Main issues: {', '.join(risk_factors)}")
```

## 🐛 Troubleshooting

**Q: All students flagged as dropout?**
A: Adjust thresholds in Config class. System may be too sensitive.

**Q: No students detected as dropout?**
A: Increase DRS weighting or lower thresholds.

**Q: LMI showing 0 for all students?**
A: Normal if students are struggling. System is working correctly.

**Q: Want to use real LLM analysis?**
A: 
```python
from openai import OpenAI
llm = OpenAI(api_key="your-key")
system = DropoutDetectionSystem(llm_client=llm)
```

## 📞 Getting Help

1. Check `README.md` for detailed documentation
2. Look at `examples.py` for usage patterns
3. Run `test_suite.py` to see all capabilities
4. Check docstrings in each module

## ✅ Checklist Before Deploying

- [ ] Read README.md
- [ ] Run main.py to see demo
- [ ] Run test_suite.py to verify
- [ ] Try an example scenario
- [ ] Understand LMI and DRS thresholds
- [ ] Configure for your use case
- [ ] Test with real student data
- [ ] Plan intervention strategy
- [ ] Train teachers on student view (supportive)
- [ ] Train teachers on teacher view (diagnostic)

## 🎯 Success Metrics

Track these to measure system effectiveness:

1. **Detection Accuracy:** % of actual dropouts caught early
2. **False Positive Rate:** % flagged who don't drop out
3. **Intervention Success:** % who recover after intervention
4. **Student Satisfaction:** Do students find feedback helpful?
5. **Teacher Satisfaction:** Is analysis actionable?

---

**Ready to go! Run `python main.py` to see it in action.** 🚀
