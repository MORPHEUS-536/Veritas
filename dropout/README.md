# Dropout Detection System - Complete Implementation

A sophisticated, multi-layered system for **detecting cognitive, behavioral, and engagement-based dropouts** during learning workflows. This system detects dropout **before failure** by observing thinking degradation, engagement decay, and behavioral drift.

## 🎯 Core Philosophy

Traditional systems detect dropout **after failure** (low marks, exam absence).

**This system detects dropout BEFORE failure** by observing:
- Thinking degradation
- Engagement decay
- Behavioral drift
- Learning momentum collapse

**Dropout is treated as a process, not an event.**

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [High-Level Definitions](#high-level-definitions)
3. [System Components](#system-components)
4. [Seven Signal Categories](#seven-signal-categories)
5. [API Usage](#api-usage)
6. [Deployment](#deployment)
7. [Ethical Constraints](#ethical-constraints)

---

## 🏗️ Architecture Overview

The system is composed of **five mandatory layers**:

```
┌─────────────────────────────────────────────────────┐
│ 5️⃣ DROPOUT CLASSIFICATION LAYER                     │
│    (Rule + Score Hybrid Logic)                      │
├─────────────────────────────────────────────────────┤
│ 4️⃣ SCORING & THRESHOLDING LAYER                    │
│    (LMI & DRS Calculation)                          │
├─────────────────────────────────────────────────────┤
│ 3️⃣ LLM ANALYSIS LAYER                              │
│    (Cognitive Reasoning Analysis)                   │
├─────────────────────────────────────────────────────┤
│ 2️⃣ FEATURE EXTRACTION LAYER                        │
│    (7 Signal Categories)                            │
├─────────────────────────────────────────────────────┤
│ 1️⃣ EVENT COLLECTION LAYER                          │
│    (Immutable, Time-Ordered Events)                 │
└─────────────────────────────────────────────────────┘
```

Each layer operates independently but feeds forward.

---

## 📖 High-Level Definitions

### What is Dropout in This System?

> A learner is considered a dropout when their **ability or intent to meaningfully continue learning** declines below a survivable threshold for a sustained duration.

This decline can occur even if the learner:
- Is logged in
- Submits answers
- Appears active

### Types of Dropout (Mandatory Classification)

#### 1. **Cognitive Dropout**
Triggered when understanding quality deteriorates.

**Indicators:**
- Shallow reasoning
- Guessing patterns
- Repeated misconceptions
- No conceptual growth across attempts

#### 2. **Behavioral Dropout**
Triggered by abnormal behavior.

**Indicators:**
- Tab switching
- Long inactivity gaps
- Abrupt answer submissions
- Erratic timing patterns

#### 3. **Engagement Dropout**
Triggered by emotional or motivational decay.

**Indicators:**
- Reduced effort
- Minimal explanations
- Rapid disengagement after failure
- Declining response richness

#### 4. **Silent Dropout (Critical)**
Most dangerous form - user appears active but learning momentum is collapsing silently.

**Indicators:**
- User appears active (events recorded)
- Answers are submitted
- Scores exist
- **Learning momentum is collapsing silently**

---

## 🔧 System Components

### 1️⃣ Event Collection Layer
**File:** `event_collector.py`

Captures raw, timestamped learning events in **immutable, time-ordered fashion**.

**Key Classes:**
- `EventCollector`: Manages immutable event recording
- `LearningEvent`: Immutable event representation

**Supported Events:**
- `QUESTION_START`: Student begins working on a question
- `QUESTION_SUBMIT`: Answer submission with correctness
- `ANSWER_REVISION`: Student revises their answer
- `NAVIGATION`: Next, back, skip actions
- `FOCUS_BLUR`: Student loses focus
- `FOCUS_FOCUS`: Student refocuses
- `HINT_REQUEST`: Student requests help
- `SESSION_START` / `SESSION_END`: Session boundaries

**Example:**
```python
collector = EventCollector()

# Record events
collector.record_question_start("STU001", "Q001", "What is 2+2?")
collector.record_question_submit("STU001", "Q001", "4", is_correct=True, time_spent_seconds=30)

# Retrieve attempt history
history = collector.build_attempt_history("STU001", "Q001")
```

### 2️⃣ Feature Extraction Layer
**File:** `feature_extractor.py`

Transforms raw events into **seven interpretable signal categories**.

**Key Class:**
- `FeatureExtractor`: Extracts comprehensive features from events

**Output:**
- `ComprehensiveFeatureSet`: All seven signal categories

**Example:**
```python
extractor = FeatureExtractor(collector)

features = extractor.extract_comprehensive_features(
    student_id="STU001",
    question_id="Q001",
    latest_mock_rank=150,
    previous_mock_rank=120
)
```

### 3️⃣ LLM Analysis Layer
**File:** `llm_analyzer.py`

Performs **cognitive reasoning analysis** using LLM on attempt history.

**Key Class:**
- `LLMAnalyzer`: Analyzes learning patterns and generates insights

**Output:**
- `AIReasoningSignals`: Structured cognitive insights

**Features:**
- Mock analysis for demonstration (no API key required)
- Real LLM integration support (OpenAI, Anthropic, etc.)
- Structured JSON outputs

**Example:**
```python
analyzer = LLMAnalyzer()  # Mock mode

history = collector.build_attempt_history("STU001", "Q001")
ai_signals = analyzer.analyze_attempt_progression(
    "STU001", "Q001", history,
    question_context="Solve: 2x + 5 = 13"
)
```

### 4️⃣ Scoring & Thresholding Layer
**File:** `scoring.py`

Calculates **Learning Momentum Index (LMI)** and **Dropout Risk Score (DRS)**.

**Key Classes:**
- `ScoringEngine`: Calculates LMI and DRS
- `ThresholdManager`: Manages decision thresholds

#### **Learning Momentum Index (LMI)**

Measures **directional improvement of thinking quality** across attempts.

**Scale:** 0-100

| Score | Status | Meaning |
|-------|--------|---------|
| > 70 | HEALTHY | Solid learning progression |
| 40-70 | AT-RISK | Declining momentum |
| < 40 | CRITICAL | Dropout trajectory |

**Key Feature:** Non-linear decay resistant to single-attempt noise.

#### **Dropout Risk Score (DRS)**

Aggregates all signals into **single actionable score**.

**Scale:** 0-1

| Score | Level | Action |
|-------|-------|--------|
| 0.0-0.3 | LOW | Monitor |
| 0.3-0.6 | MEDIUM | Proactive support |
| 0.6-0.8 | HIGH | Intervention recommended |
| 0.8-1.0 | CRITICAL | Immediate intervention |

**Example:**
```python
scoring = ScoringEngine()

lmi = scoring.calculate_lmi(features)
print(f"LMI: {lmi.lmi_score:.1f}/100")

drs = scoring.calculate_drs(features)
print(f"DRS: {drs.drs_score:.2f}/1.0 ({drs.risk_level})")
```

### 5️⃣ Dropout Classification Layer
**File:** `dropout_classifier.py`

Implements **rule + score hybrid logic** for classification.

**Key Classes:**
- `DropoutClassifier`: Classifies dropout types
- `DropoutDetectionPipeline`: Orchestrates all layers

**Output:**
- `DropoutClassification`: Final classification with types and recommendations

**Example:**
```python
classifier = DropoutClassifier(scoring_engine)

classification = classifier.classify(features)

print(f"Is Dropout: {classification.is_dropout}")
print(f"Types: {[dt.value for dt in classification.dropout_types]}")
print(f"Reason: {classification.primary_reason}")
print(f"Recommendation: {classification.recommendation}")
```

### 🎨 Main Orchestrator & Views
**File:** `main.py`

Complete system integration with **Teacher and Student views**.

**Key Classes:**
- `StudentView`: Supportive, non-judgmental feedback
- `TeacherView`: Full dropout analysis and metrics
- `DropoutDetectionSystem`: Main orchestrator

---

## 📊 Seven Signal Categories

### 1️⃣ **Learning Progress Signals (PRIMARY)**

Answers: "Is the student actually moving forward?"

**Parameters:**
- `attempt_count`: Total attempts on question
- `attempt_frequency`: Attempts per minute
- `time_spent_per_attempt`: List of durations
- `improvement_score`: 0-100 based on correctness progression
- `change_type`: SUPERFICIAL | STRUCTURAL | CORRECTIVE
- `semantic_change_score`: 0-100 (meaningful changes)
- `learning_state`: PROGRESSING | PLATEAU | STALLED
- `no_progress_flag`: True if semantic improvement < 30% after 3+ attempts

**Why They Matter:**
> Dropout begins when effort stops translating into progress

### 2️⃣ **Stagnation Signals (MOST IMPORTANT)**

Answers: "Is the student stuck for too long?"

**Parameters:**
- `stagnation_duration_minutes`: Time spent on single problem
- `repeat_attempt_count`: Number of attempts
- `concept_revisit_frequency`: How many times revisited
- `is_stalled`: True if (attempts >= 3 AND duration >= 15 mins AND improvement < threshold)
- `stagnation_severity`: 0-100

**Why This Matters:**
> Dropout is time-based, not score-based. Long struggle without progress = confidence collapse.

### 3️⃣ **Integrity & Authenticity Signals (SUPPORTING)**

Answers: "Does this learning look consistent and authentic?"

**Parameters:**
- `integrity_score`: 0-100
- `reasoning_continuity`: HIGH | MEDIUM | LOW
- `sudden_jump_flag`: Unexplained correctness jump
- `external_assistance_likelihood`: 0-1

**⚠️ Important Rule:**
> Integrity signals **never alone** trigger dropout. They amplify other risk signals.

### 4️⃣ **AI Reasoning & Explanation Signals (INTERPRETIVE)**

Answers: "Why is the student struggling?"

**Parameters:**
- `conceptual_gap_description`: What concept is missing
- `learning_summary`: Progress narrative
- `llm_confidence_estimate`: 0-1
- `misconception_patterns`: List of detected patterns
- `confidence_vs_correctness_gap`: -50 to +50

**Role of AI:**
> AI **does not decide** dropout. AI **explains** where student is stuck and what help is needed.

### 5️⃣ **Competition-Aware Signals (NOVEL - India Context)**

Answers: "Is competition causing disengagement?"

**Parameters:**
- `latest_mock_rank`: Current rank
- `previous_mock_rank`: Previous rank
- `rank_delta`: Rank change (negative = improved)
- `relative_progress_index`: 0-100
- `competition_pressure_flag`: True if pressure detected

**Why This Matters:**
> JEE/NEET dropout often happens due to rank comparison and mock test pressure.

### 6️⃣ **Behavioral Disengagement Signals**

Answers: "Is effort reducing over time?"

**Parameters:**
- `attempt_gap_time`: Seconds between attempts
- `daily_attempt_count`: Attempts per day
- `consistency_score`: 0-100
- `average_gap_increasing`: True if gaps getting longer

**Meaning:**
> Longer gaps between attempts + reduced daily effort = silent disengagement

### 7️⃣ **Intervention Response Signals (POST-DETECTION)**

Answers: "Did intervention help?"

**Parameters:**
- `intervention_triggered`: Whether intervention was started
- `intervention_type`: Type of support given
- `post_intervention_progress`: 0-100
- `recovery_score`: 0-100
- `intervention_success_flag`: True if helpful

**Used to:**
- Lower dropout risk after intervention
- Validate system effectiveness

---

## 🚀 API Usage

### Basic Usage

```python
from main import DropoutDetectionSystem, UserRole

# Initialize system
system = DropoutDetectionSystem()

# Record learning events
system.record_event(
    event_type=EventType.QUESTION_SUBMIT,
    student_id="STU001",
    question_id="Q001",
    data={
        "answer": "x = 4",
        "is_correct": True,
        "time_spent_seconds": 120
    }
)

# Analyze and get Teacher view
teacher_report = system.analyze(
    "STU001", "Q001",
    question_context="Solve: 2x + 5 = 13",
    role=UserRole.TEACHER
)

print(f"Status: {teacher_report['dropout_status']}")
print(f"LMI: {teacher_report['scores']['lmi']['score']}")
print(f"DRS: {teacher_report['scores']['drs']['score']}")

# Analyze and get Student view
student_report = system.analyze(
    "STU001", "Q001",
    question_context="Solve: 2x + 5 = 13",
    role=UserRole.STUDENT
)

print(f"Encouragement: {student_report['encouragement']}")
```

### Advanced: Direct Pipeline Usage

```python
from event_collector import EventCollector
from feature_extractor import FeatureExtractor
from llm_analyzer import LLMAnalyzer
from dropout_classifier import DropoutDetectionPipeline

# Set up layers
collector = EventCollector()
extractor = FeatureExtractor(collector)
analyzer = LLMAnalyzer()
pipeline = DropoutDetectionPipeline(collector, extractor, analyzer)

# Analyze
features, classification = pipeline.analyze_student_question(
    "STU001", "Q001"
)

print(classification)
```

---

## 📦 Deployment

### Installation

```bash
# No external dependencies required for mock mode
python main.py

# For LLM integration (optional)
pip install openai
```

### Files Structure

```
dropout/
├── models.py                    # Data structures and enums
├── event_collector.py          # Layer 1: Event collection
├── feature_extractor.py        # Layer 2: Feature extraction
├── llm_analyzer.py             # Layer 3: LLM analysis
├── scoring.py                  # Layer 4: Scoring
├── dropout_classifier.py       # Layer 5: Classification
├── main.py                     # Orchestrator & views
└── README.md                   # This file
```

### Configuration

To enable real LLM analysis, pass an LLM client:

```python
from openai import OpenAI

llm_client = OpenAI(api_key="your-api-key")
system = DropoutDetectionSystem(llm_client=llm_client)
```

---

## 🌍 Ethical Constraints

This system prioritizes **supportive, not judgmental** interventions.

### Student-Facing Rules

- ✓ Never show "dropout" labels to students
- ✓ Show encouragement signals
- ✓ Show adaptive difficulty adjustments
- ✓ Frame challenges as opportunities

### Teacher-Facing Rules

- ✓ Full dropout classification
- ✓ LMI trend graphs and analysis
- ✓ Risk explanations with evidence
- ✓ Intervention recommendations

### System-Level Constraints

- ✗ No punitive actions
- ✗ No automated disqualification
- ✓ Dropout detection is **supportive, not judgmental**
- ✓ All interventions are **supportive** not **punitive**

---

## 📈 Example Outputs

### Teacher View Example

```
Status: ✓ NO_DROPOUT
Confidence: 74%

Learning Momentum Index (LMI): 14.2/100 - CRITICAL
Dropout Risk Score (DRS): 0.40/1.0 - MEDIUM

Recommendation: Continue monitoring. No immediate intervention needed.

Signals:
- Learning Progress: 2 attempts, 33% improvement
- Stagnation: 5 minutes, is_stalled=False
- Behavioral: Consistency 100%
```

### Student View Example

```
💪 Your Strengths:
  • Great persistence - you're working through challenges.
  • Your engagement is consistent and focused.

📈 Growth Areas:
  • Try a Different Approach: You've been on this problem for 5 minutes.
    Sometimes stepping back and viewing differently helps.

Next Steps: Keep practicing at this level - you'll break through soon.

Encouragement: "Your persistence is impressive. Keep it up!"
```

---

## 🔬 System Design Principles

1. **Layered Architecture**: Each layer independent, composable
2. **Immutable Events**: Events cannot be modified (data integrity)
3. **Time-Ordered**: All events strictly chronological
4. **Non-Judgmental**: Supportive language throughout
5. **Multi-Signal**: No single metric decides dropout
6. **Explainable**: Every decision has clear reasoning
7. **Privacy-Preserving**: Works with aggregated features
8. **Early Detection**: Catches dropout before failure

---

## 📚 References

- **JEE/NEET Context**: System specifically designed for Indian competitive exam prep
- **Cognitive Science**: Learning momentum based on cognitive load theory
- **Behavioral Patterns**: Evidence-based behavioral markers of disengagement
- **Ethical AI**: Designed to support, not punish

---

## 🤝 Contributing

This system is designed to be extended. Key extension points:

1. **Better LLM Analysis**: Replace mock analyzer with real LLM
2. **More Event Types**: Add custom event types for your domain
3. **Ranking Systems**: Integrate real mock test ranking data
4. **Intervention Tracking**: Track and measure intervention effectiveness
5. **Visualization**: Build dashboards on top of signals

---

## 📝 License

Open source - available for educational and research purposes.

---

## ❓ FAQ

**Q: Does this system require real-time events?**
A: No. It can batch-process historical data. Events are collected and analyzed asynchronously.

**Q: What if a student appears dropout but actually isn't?**
A: The confidence metric quantifies uncertainty. Lower confidence triggers "monitor" instead of "intervene".

**Q: Can this be gamed?**
A: The system is resistant to simple gaming:
  - Multiple semantic signals must align
  - Integrity checks detect sudden jumps
  - Time-based metrics catch rushing
  - Behavioral consistency is required

**Q: How often should we analyze?**
A: Recommend after every 3-5 attempts or daily at minimum for consistent monitoring.

**Q: Is this system accurate?**
A: The confidence scores reflect actual uncertainty. System is conservative - prefers false negatives to false positives (supportive approach).

---

**Built with ❤️ for learning support**
