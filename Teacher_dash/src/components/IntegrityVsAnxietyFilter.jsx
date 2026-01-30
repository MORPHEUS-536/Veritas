import { Card, CardContent, CardHeader, CardTitle } from './ui/card'

export default function IntegrityVsAnxietyFilter({ students }) {
  // Filter students by integrity and competition pressure
  const categorizedStudents = {
    anxious: students.filter(s => s.integrityScore < 60 && s.competitionPressureFlag),
    cheating: students.filter(s => s.integrityScore < 60 && !s.competitionPressureFlag),
    confident: students.filter(s => s.integrityScore >= 80),
    consistent: students.filter(s => s.integrityScore >= 60 && s.integrityScore < 80)
  }

  const getCategory = (integrityScore, competitionPressure) => {
    if (integrityScore < 60 && competitionPressure) return 'Performance Anxiety'
    if (integrityScore < 60 && !competitionPressure) return 'Potential Integrity Issue'
    if (integrityScore >= 80) return 'High Confidence'
    return 'Consistent Performer'
  }

  const getCategoryColor = (category) => {
    switch(category) {
      case 'Performance Anxiety': return { bg: 'rgba(251, 146, 60, 0.1)', border: 'rgba(251, 146, 60, 0.3)', text: '#fb923c' }
      case 'Potential Integrity Issue': return { bg: 'rgba(239, 68, 68, 0.1)', border: 'rgba(239, 68, 68, 0.3)', text: '#ef4444' }
      case 'High Confidence': return { bg: 'rgba(74, 222, 128, 0.1)', border: 'rgba(74, 222, 128, 0.3)', text: '#4ade80' }
      default: return { bg: 'rgba(96, 165, 250, 0.1)', border: 'rgba(96, 165, 250, 0.3)', text: '#60a5fa' }
    }
  }

  const getCategoryAction = (category) => {
    switch(category) {
      case 'Performance Anxiety': return '💪 Provide encouragement & peer support. Review their logic—it\'s solid!'
      case 'Potential Integrity Issue': return '⚠️ Manual review required. Check for copy-paste or external tool usage.'
      case 'High Confidence': return '🌟 Encourage to mentor struggling peers or tackle advanced topics.'
      default: return '✅ Monitor progress. Encourage consistency.'
    }
  }

  const allCategorizedStudents = [
    ...categorizedStudents.anxious.map(s => ({ ...s, category: 'Performance Anxiety' })),
    ...categorizedStudents.cheating.map(s => ({ ...s, category: 'Potential Integrity Issue' })),
    ...categorizedStudents.confident.map(s => ({ ...s, category: 'High Confidence' })),
    ...categorizedStudents.consistent.map(s => ({ ...s, category: 'Consistent Performer' }))
  ]

  return (
    <Card style={{
      backgroundColor: 'rgba(15, 23, 42, 0.6)',
      border: '1px solid rgba(71, 85, 105, 0.5)',
      borderRadius: '0.5rem'
    }}>
      <CardHeader>
        <CardTitle style={{ color: '#f1f5f9', fontSize: '1.125rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          🎭 Integrity vs. Anxiety Analysis
        </CardTitle>
        <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginTop: '0.5rem' }}>
          Distinguish between performance anxiety and academic integrity concerns
        </p>
      </CardHeader>
      <CardContent>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem', maxHeight: '400px', overflowY: 'auto' }}>
          {allCategorizedStudents.slice(0, 12).map((student) => {
            const colors = getCategoryColor(student.category)
            return (
              <div
                key={student.id}
                style={{
                  padding: '1rem',
                  backgroundColor: colors.bg,
                  border: `1px solid ${colors.border}`,
                  borderRadius: '0.375rem'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                  <div>
                    <p style={{ fontSize: '0.875rem', fontWeight: '600', color: '#f1f5f9' }}>
                      {student.name}
                    </p>
                    <p style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                      Integrity: {student.integrityScore}
                    </p>
                  </div>
                  <span style={{
                    padding: '0.25rem 0.5rem',
                    borderRadius: '9999px',
                    backgroundColor: colors.text,
                    color: '#0f172a',
                    fontSize: '0.65rem',
                    fontWeight: '600'
                  }}>
                    {student.category}
                  </span>
                </div>
                <p style={{ fontSize: '0.75rem', color: '#cbd5e1', marginBottom: '0.5rem', lineHeight: '1.4' }}>
                  {getCategoryAction(student.category)}
                </p>
              </div>
            )
          })}
        </div>
        {allCategorizedStudents.length > 12 && (
          <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '1rem', textAlign: 'center' }}>
            Showing 12 of {allCategorizedStudents.length} students. Scroll to see more.
          </p>
        )}
      </CardContent>
    </Card>
  )
}
