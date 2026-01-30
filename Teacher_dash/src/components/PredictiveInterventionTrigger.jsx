import { Card, CardContent, CardHeader, CardTitle } from './ui/card'

export default function PredictiveInterventionTrigger({ students }) {
  // Filter students with high reasoning continuity but dropping confidence
  const impostorSyndromeStudents = students.filter(s => 
    s.reasoningContinuity === 'HIGH' && s.confidenceDropSignal
  )

  const stagnatedStudents = students.filter(s =>
    s.stagnationDurationMinutes > 15 && !s.impostorSyndrome
  )

  const burnoutRiskStudents = students.filter(s =>
    s.stagnationDurationMinutes > 20 && s.dayOfWeek === 'Friday'
  )

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '1.5rem' }}>
      {/* Imposter Syndrome Detection */}
      <Card style={{
        backgroundColor: 'rgba(15, 23, 42, 0.6)',
        border: '1px solid rgba(167, 139, 250, 0.3)',
        borderRadius: '0.5rem'
      }}>
        <CardHeader>
          <CardTitle style={{ color: '#a78bfa', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            🎓 Imposter Syndrome Detection
          </CardTitle>
        </CardHeader>
        <CardContent>
          {impostorSyndromeStudents.length > 0 ? (
            <div style={{ display: 'grid', gap: '0.75rem', maxHeight: '300px', overflowY: 'auto' }}>
              {impostorSyndromeStudents.slice(0, 5).map(student => (
                <div key={student.id} style={{
                  padding: '0.75rem',
                  backgroundColor: 'rgba(167, 139, 250, 0.1)',
                  border: '1px solid rgba(167, 139, 250, 0.2)',
                  borderRadius: '0.375rem'
                }}>
                  <p style={{ fontSize: '0.875rem', fontWeight: '600', color: '#f1f5f9', marginBottom: '0.25rem' }}>
                    {student.name}
                  </p>
                  <p style={{ fontSize: '0.75rem', color: '#cbd5e1', marginBottom: '0.5rem' }}>
                    Reasoning: HIGH ✓ | Confidence: DROPPING ↓
                  </p>
                  <div style={{
                    padding: '0.5rem',
                    backgroundColor: 'rgba(167, 139, 250, 0.15)',
                    borderRadius: '0.25rem',
                    borderLeft: '2px solid #a78bfa'
                  }}>
                    <p style={{ fontSize: '0.75rem', color: '#cbd5e1', fontStyle: 'italic' }}>
                      "You've got the logic down perfectly, don't second-guess your steps!"
                    </p>
                  </div>
                </div>
              ))}
              {impostorSyndromeStudents.length > 5 && (
                <p style={{ fontSize: '0.75rem', color: '#94a3b8', textAlign: 'center', marginTop: '0.5rem' }}>
                  +{impostorSyndromeStudents.length - 5} more students
                </p>
              )}
            </div>
          ) : (
            <p style={{ fontSize: '0.875rem', color: '#94a3b8', textAlign: 'center', padding: '1rem' }}>
              ✅ No students detected with imposter syndrome patterns
            </p>
          )}
        </CardContent>
      </Card>

      {/* Stagnation Alert */}
      <Card style={{
        backgroundColor: 'rgba(15, 23, 42, 0.6)',
        border: '1px solid rgba(250, 204, 21, 0.3)',
        borderRadius: '0.5rem'
      }}>
        <CardHeader>
          <CardTitle style={{ color: '#fbbf24', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            ⏸️ Stagnation Detection
          </CardTitle>
        </CardHeader>
        <CardContent>
          {stagnatedStudents.length > 0 ? (
            <div style={{ display: 'grid', gap: '0.75rem', maxHeight: '300px', overflowY: 'auto' }}>
              {stagnatedStudents.slice(0, 5).map(student => (
                <div key={student.id} style={{
                  padding: '0.75rem',
                  backgroundColor: 'rgba(250, 204, 21, 0.1)',
                  border: '1px solid rgba(250, 204, 21, 0.2)',
                  borderRadius: '0.375rem'
                }}>
                  <p style={{ fontSize: '0.875rem', fontWeight: '600', color: '#f1f5f9', marginBottom: '0.25rem' }}>
                    {student.name}
                  </p>
                  <p style={{ fontSize: '0.75rem', color: '#cbd5e1', marginBottom: '0.5rem' }}>
                    Stuck for {student.stagnationDurationMinutes} minutes on: <span style={{ fontWeight: '600' }}>{student.conceptName}</span>
                  </p>
                  <button style={{
                    width: '100%',
                    padding: '0.5rem',
                    backgroundColor: '#fbbf24',
                    color: '#0f172a',
                    borderRadius: '0.25rem',
                    border: 'none',
                    fontSize: '0.75rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#facc15'
                    e.currentTarget.style.transform = 'scale(1.02)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = '#fbbf24'
                    e.currentTarget.style.transform = 'scale(1)'
                  }}>
                    Send Quick Hint
                  </button>
                </div>
              ))}
              {stagnatedStudents.length > 5 && (
                <p style={{ fontSize: '0.75rem', color: '#94a3b8', textAlign: 'center', marginTop: '0.5rem' }}>
                  +{stagnatedStudents.length - 5} more students
                </p>
              )}
            </div>
          ) : (
            <p style={{ fontSize: '0.875rem', color: '#94a3b8', textAlign: 'center', padding: '1rem' }}>
              ✅ No students currently stagnating
            </p>
          )}
        </CardContent>
      </Card>

      {/* Burnout Prediction */}
      <Card style={{
        backgroundColor: 'rgba(15, 23, 42, 0.6)',
        border: '1px solid rgba(239, 68, 68, 0.3)',
        borderRadius: '0.5rem'
      }}>
        <CardHeader>
          <CardTitle style={{ color: '#ef4444', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            🔥 Burnout Risk Assessment
          </CardTitle>
        </CardHeader>
        <CardContent>
          {burnoutRiskStudents.length > 0 ? (
            <div style={{ display: 'grid', gap: '0.75rem', maxHeight: '300px', overflowY: 'auto' }}>
              {burnoutRiskStudents.slice(0, 5).map(student => (
                <div key={student.id} style={{
                  padding: '0.75rem',
                  backgroundColor: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid rgba(239, 68, 68, 0.2)',
                  borderRadius: '0.375rem'
                }}>
                  <p style={{ fontSize: '0.875rem', fontWeight: '600', color: '#f1f5f9', marginBottom: '0.25rem' }}>
                    {student.name}
                  </p>
                  <p style={{ fontSize: '0.75rem', color: '#cbd5e1', marginBottom: '0.5rem' }}>
                    High stagnation late in week ({student.stagnationDurationMinutes}min)
                  </p>
                  <div style={{
                    padding: '0.5rem',
                    backgroundColor: 'rgba(239, 68, 68, 0.15)',
                    borderRadius: '0.25rem',
                    borderLeft: '2px solid #ef4444'
                  }}>
                    <p style={{ fontSize: '0.75rem', color: '#fca5a5' }}>
                      💡 Suggest low-cognitive load review tasks or a break
                    </p>
                  </div>
                </div>
              ))}
              {burnoutRiskStudents.length > 5 && (
                <p style={{ fontSize: '0.75rem', color: '#94a3b8', textAlign: 'center', marginTop: '0.5rem' }}>
                  +{burnoutRiskStudents.length - 5} more students
                </p>
              )}
            </div>
          ) : (
            <p style={{ fontSize: '0.875rem', color: '#94a3b8', textAlign: 'center', padding: '1rem' }}>
              ✅ No burnout risk detected
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
