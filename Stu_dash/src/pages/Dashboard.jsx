import { useEffect, useState } from 'react'
import Header from '../components/Header'
import ProofOfThought from '../components/ProofOfThought'
import CognitiveAptitude from '../components/CognitiveAptitude'
import CurrentAssignment from '../components/CurrentAssignment'
import ActionCards from '../components/ActionCards'
import { dbService } from '../services/DatabaseService'
import { useIntegrityTracking } from '../hooks/useIntegrityTracking'

export default function Dashboard() {
  const [studentData, setStudentData] = useState({
    id: 'student_001',
    integrityScore: 85,
    studentName: 'Alex Johnson',
    email: 'alex.johnson@veritas.edu',
    assignments: [
      {
        id: 1,
        title: 'Philosophy of Logic',
        description: 'Analyze the philosophical implications of logical reasoning',
        instructions: `Instructions for Philosophy of Logic:

1. Read the provided philosophical texts on logic and reasoning
2. Identify key arguments and fallacies
3. Create a logical tree diagram showing argument structure
4. Document your thought process through voice notes
5. Submit initial draft for peer review

Detailed Instructions:
- Focus on understanding the difference between deductive and inductive reasoning
- Consider real-world applications of logical principles
- Look for common logical fallacies in everyday arguments
- Create a comprehensive framework for critical thinking
- Record voice reflections after each study session
- Update drafts based on feedback from instructors and peers

Grading Criteria:
- Understanding of core concepts (25%)
- Quality of logical analysis (25%)
- Clarity of presentation (20%)
- Depth of thought evolution (20%)
- Academic integrity (10%)`
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
    ]
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
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <Header studentName={studentData.studentName} integrityScore={studentData.integrityScore} />
      
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Top Metrics Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-1">
            <ProofOfThought score={studentData.integrityScore} />
          </div>
          <div className="lg:col-span-2">
            <CognitiveAptitude data={studentData.cognitiveProfile} />
          </div>
        </div>

        {/* Current Assignment Section */}
        <div className="mb-8">
          <CurrentAssignment assignment={studentData.assignments[0]} />
        </div>

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
