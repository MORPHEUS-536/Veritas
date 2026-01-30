import { useEffect, useState } from 'react'
import Header from '../components/Header'
import ProofOfThought from '../components/ProofOfThought'
import CognitiveAptitude from '../components/CognitiveAptitude'
import CurrentAssignment from '../components/CurrentAssignment'
import ActionCards from '../components/ActionCards'
import ProgressAndReasoning from '../components/ProgressAndReasoning'
import IntegrityPanel from '../components/IntegrityPanel'
import StagnationDetection from '../components/StagnationDetection'
import ResponseStrategies from '../components/ResponseStrategies'
import { dbService } from '../services/DatabaseService'
import { useIntegrityTracking } from '../hooks/useIntegrityTracking'

export default function Dashboard() {
  const [selectedConceptId, setSelectedConceptId] = useState('concept_001')
  
  const [studentData, setStudentData] = useState({
    id: 'student_001',
    integrityScore: 85,
    studentName: 'Alex Johnson',
    email: 'alex.johnson@veritas.edu',
    assignments: [
      {
        id: 1,
        title: 'Select the concepts',
        description: 'Choose a concept from the list below to begin your learning journey',
        instructions: ''
      }
    ],
    workstreams: [
      {
        id: 1,
        name: 'Logic Tree Canvas',
        icon: '🌳',
        description: 'Visualize your logical arguments',
        progress: 45,
        status: 'in-progress',
        lastUpdated: '2 hours ago'
      },
      {
        id: 2,
        name: 'Voice Reflections',
        icon: '🎙️',
        description: 'Record your thought process',
        progress: 30,
        status: 'not-started',
        lastUpdated: null
      },
      {
        id: 3,
        name: 'Draft History',
        icon: '📝',
        description: 'Track your draft evolution',
        progress: 65,
        status: 'in-progress',
        lastUpdated: '30 minutes ago'
      }
    ],
    cognitiveProfile: [
      { name: 'Analytical', value: 85 },
      { name: 'Creative', value: 72 },
      { name: 'Critical', value: 88 },
      { name: 'Synthesis', value: 76 },
      { name: 'Evaluation', value: 82 }
    ],
    concepts: [
      {
        concept_id: 'concept_001',
        concept_name: 'Deductive Reasoning',
        subject: 'Philosophy',
        difficulty_level: 2,
        attempt_count: 3
      },
      {
        concept_id: 'concept_002',
        concept_name: 'Inductive Reasoning',
        subject: 'Philosophy',
        difficulty_level: 3,
        attempt_count: 1
      },
      {
        concept_id: 'concept_003',
        concept_name: 'Logical Fallacies',
        subject: 'Philosophy',
        difficulty_level: 3,
        attempt_count: 2
      },
      {
        concept_id: 'concept_004',
        concept_name: 'Critical Thinking Framework',
        subject: 'Philosophy',
        difficulty_level: 4,
        attempt_count: 0
      },
      {
        concept_id: 'concept_005',
        concept_name: 'Epistemology',
        subject: 'Philosophy',
        difficulty_level: 4,
        attempt_count: 1
      },
      {
        concept_id: 'concept_006',
        concept_name: 'Algebra Fundamentals',
        subject: 'Mathematics',
        difficulty_level: 1,
        attempt_count: 5
      },
      {
        concept_id: 'concept_007',
        concept_name: 'Calculus Basics',
        subject: 'Mathematics',
        difficulty_level: 3,
        attempt_count: 2
      },
      {
        concept_id: 'concept_008',
        concept_name: 'Linear Equations',
        subject: 'Mathematics',
        difficulty_level: 2,
        attempt_count: 4
      },
      {
        concept_id: 'concept_009',
        concept_name: 'Probability Theory',
        subject: 'Mathematics',
        difficulty_level: 4,
        attempt_count: 0
      },
      {
        concept_id: 'concept_010',
        concept_name: 'Cell Biology',
        subject: 'Biology',
        difficulty_level: 2,
        attempt_count: 2
      },
      {
        concept_id: 'concept_011',
        concept_name: 'Genetics',
        subject: 'Biology',
        difficulty_level: 3,
        attempt_count: 1
      },
      {
        concept_id: 'concept_012',
        concept_name: 'Evolution',
        subject: 'Biology',
        difficulty_level: 4,
        attempt_count: 0
      },
      {
        concept_id: 'concept_013',
        concept_name: 'Ecosystem Dynamics',
        subject: 'Biology',
        difficulty_level: 3,
        attempt_count: 1
      },
      {
        concept_id: 'concept_014',
        concept_name: 'Kinematics',
        subject: 'Physics',
        difficulty_level: 2,
        attempt_count: 3
      },
      {
        concept_id: 'concept_015',
        concept_name: 'Newton\'s Laws',
        subject: 'Physics',
        difficulty_level: 2,
        attempt_count: 2
      },
      {
        concept_id: 'concept_016',
        concept_name: 'Thermodynamics',
        subject: 'Physics',
        difficulty_level: 4,
        attempt_count: 0
      },
      {
        concept_id: 'concept_017',
        concept_name: 'Quantum Mechanics',
        subject: 'Physics',
        difficulty_level: 5,
        attempt_count: 0
      },
      {
        concept_id: 'concept_018',
        concept_name: 'Constitutional Law',
        subject: 'Law',
        difficulty_level: 4,
        attempt_count: 1
      },
      {
        concept_id: 'concept_019',
        concept_name: 'Contract Law',
        subject: 'Law',
        difficulty_level: 3,
        attempt_count: 2
      },
      {
        concept_id: 'concept_020',
        concept_name: 'Criminal Law Basics',
        subject: 'Law',
        difficulty_level: 3,
        attempt_count: 0
      }
    ],
    learningMetrics: {
      learning_progress_score: 68,
      semantic_change_score: 0.72,
      reasoning_continuity: 'HIGH',
      integrity_score: 0.92,
      sudden_jump_flag: false,
      integrity_status_label: 'CONSISTENT',
      stagnation_duration_minutes: 12,
      repeat_attempt_count: 2,
      no_progress_flag: false,
      learning_state: 'PROGRESSING',
      dropout_risk_level: 'LOW'
    }
  })

  const [loading, setLoading] = useState(false)
  const { trackAction, updateScore, recordWorkstreamProgress } = useIntegrityTracking()

  const handleActionClick = async (workstreamId, action) => {
    setLoading(true)
    
    try {
      // Track the action in database
      await trackAction(studentData.id, `workstream_${action}`, {
        workstreamId,
        action,
        timestamp: new Date().toISOString()
      })

      const workstream = studentData.workstreams.find(w => w.id === workstreamId)
      if (workstream) {
        const updatedWorkstreams = studentData.workstreams.map(w => {
          if (w.id === workstreamId) {
            return {
              ...w,
              status: action === 'start' ? 'in-progress' : 'in-progress',
              progress: Math.min(w.progress + 15, 100),
              lastUpdated: 'just now'
            }
          }
          return w
        })

        const newScore = Math.min(85 + (updatedWorkstreams.filter(w => w.progress === 100).length * 2), 100)

        // Record workstream progress in database
        await recordWorkstreamProgress(
          studentData.id,
          workstreamId,
          updatedWorkstreams.find(w => w.id === workstreamId).progress,
          updatedWorkstreams.find(w => w.id === workstreamId).status
        )

        // Update integrity score in database
        await updateScore(studentData.id, newScore)

        setStudentData(prev => ({
          ...prev,
          workstreams: updatedWorkstreams,
          integrityScore: newScore
        }))
      }
    } catch (error) {
      console.error('Error updating workstream:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0f172a', color: '#f1f5f9' }}>
      <Header studentName={studentData.studentName} integrityScore={studentData.integrityScore} />
      
      <main style={{ maxWidth: '1400px', margin: '0 auto', padding: '2rem 1rem' }}>
        {/* Top Metrics Row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
          <div>
            <ProofOfThought score={studentData.integrityScore} />
          </div>
          <div>
            <CognitiveAptitude data={studentData.cognitiveProfile} />
          </div>
        </div>

        {/* Current Assignment Section with Integrated Concept Selector */}
        <CurrentAssignment 
          assignment={studentData.assignments[0]}
          concepts={studentData.concepts}
          selectedConceptId={selectedConceptId}
          onSelectConcept={setSelectedConceptId}
        />

        {/* Adaptive Learning Panel - 3 Column Layout */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
          <ProgressAndReasoning 
            learningProgress={studentData.learningMetrics.learning_progress_score}
            semanticChange={studentData.learningMetrics.semantic_change_score}
            reasoningContinuity={studentData.learningMetrics.reasoning_continuity}
          />
          <IntegrityPanel 
            integrityScore={studentData.learningMetrics.integrity_score}
            suddenJumpFlag={studentData.learningMetrics.sudden_jump_flag}
            integrityStatusLabel={studentData.learningMetrics.integrity_status_label}
          />
          <StagnationDetection 
            stagnationDurationMinutes={studentData.learningMetrics.stagnation_duration_minutes}
            repeatAttemptCount={studentData.learningMetrics.repeat_attempt_count}
            noProgressFlag={studentData.learningMetrics.no_progress_flag}
            learningState={studentData.learningMetrics.learning_state}
            dropoutRiskLevel={studentData.learningMetrics.dropout_risk_level}
          />
        </div>

        {/* Dynamic Response Strategies */}
        <ResponseStrategies 
          learningState={studentData.learningMetrics.learning_state}
          currentConcept={studentData.concepts.find(c => c.concept_id === selectedConceptId)}
        />

        {/* Action Cards */}
        <ActionCards 
          workstreams={studentData.workstreams}
          onActionClick={handleActionClick}
          isLoading={loading}
        />
      </main>
    </div>
  )
}
