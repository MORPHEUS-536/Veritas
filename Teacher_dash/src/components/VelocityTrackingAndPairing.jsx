import { Card, CardContent, CardHeader, CardTitle } from './ui/card'

export default function VelocityTrackingAndPairing({ students }) {
  // Calculate velocity: Progress / Time (assuming time is stagnation duration inversely)
  const velocityStudents = students.map(student => {
    const velocity = student.learningProgressScore / Math.max(student.stagnationDurationMinutes, 1)
    return { ...student, velocity }
  }).sort((a, b) => b.velocity - a.velocity)

  const speedRunners = velocityStudents.filter(s => s.velocity > 5).slice(0, 5)
  const slowPace = velocityStudents.filter(s => s.velocity < 2).slice(0, 5)

  // Social Learning Pairing: Match high continuity with stalled on same concept
  const conceptGroups = {}
  students.forEach(student => {
    if (!conceptGroups[student.conceptName]) {
      conceptGroups[student.conceptName] = { high: [], stalled: [] }
    }
    if (student.reasoningContinity === 'HIGH' || student.learningState === 'PROGRESSING') {
      conceptGroups[student.conceptName].high.push(student)
    } else if (student.learningState === 'STALLED') {
      conceptGroups[student.conceptName].stalled.push(student)
    }
  })

  const pairingOpportunities = []
  Object.entries(conceptGroups).forEach(([concept, groups]) => {
    if (groups.high.length > 0 && groups.stalled.length > 0) {
      pairingOpportunities.push({
        concept,
        mentor: groups.high[0],
        mentee: groups.stalled[0]
      })
    }
  })

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '1.5rem' }}>
      {/* Velocity Tracking */}
      <Card style={{
        backgroundColor: 'rgba(15, 23, 42, 0.6)',
        border: '1px solid rgba(96, 165, 250, 0.3)',
        borderRadius: '0.5rem'
      }}>
        <CardHeader>
          <CardTitle style={{ color: '#60a5fa', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            ⚡ Velocity Tracking
          </CardTitle>
          <p style={{ color: '#94a3b8', fontSize: '0.75rem', marginTop: '0.5rem' }}>
            Identify speed-runners and students who need pacing support
          </p>
        </CardHeader>
        <CardContent>
          <div style={{ display: 'grid', gap: '1rem' }}>
            <div>
              <p style={{ fontSize: '0.875rem', fontWeight: '600', color: '#f1f5f9', marginBottom: '0.75rem' }}>
                🚀 Speed-Runners (High Velocity)
              </p>
              <div style={{ display: 'grid', gap: '0.5rem', maxHeight: '200px', overflowY: 'auto' }}>
                {speedRunners.length > 0 ? (
                  speedRunners.map(student => (
                    <div key={student.id} style={{
                      padding: '0.75rem',
                      backgroundColor: 'rgba(96, 165, 250, 0.1)',
                      border: '1px solid rgba(96, 165, 250, 0.2)',
                      borderRadius: '0.375rem',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}>
                      <div>
                        <p style={{ fontSize: '0.875rem', fontWeight: '600', color: '#f1f5f9' }}>
                          {student.name}
                        </p>
                        <p style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                          Velocity: {student.velocity.toFixed(2)} (might be bored)
                        </p>
                      </div>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        backgroundColor: '#60a5fa',
                        color: '#0f172a',
                        borderRadius: '9999px',
                        fontSize: '0.7rem',
                        fontWeight: '600'
                      }}>
                        🌟
                      </span>
                    </div>
                  ))
                ) : (
                  <p style={{ fontSize: '0.75rem', color: '#94a3b8' }}>No speed-runners detected</p>
                )}
              </div>
            </div>

            <div>
              <p style={{ fontSize: '0.875rem', fontWeight: '600', color: '#f1f5f9', marginBottom: '0.75rem' }}>
                🐢 Slow Pace (Need Support)
              </p>
              <div style={{ display: 'grid', gap: '0.5rem', maxHeight: '200px', overflowY: 'auto' }}>
                {slowPace.length > 0 ? (
                  slowPace.map(student => (
                    <div key={student.id} style={{
                      padding: '0.75rem',
                      backgroundColor: 'rgba(250, 204, 21, 0.1)',
                      border: '1px solid rgba(250, 204, 21, 0.2)',
                      borderRadius: '0.375rem',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}>
                      <div>
                        <p style={{ fontSize: '0.875rem', fontWeight: '600', color: '#f1f5f9' }}>
                          {student.name}
                        </p>
                        <p style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                          Velocity: {student.velocity.toFixed(2)} (may need scaffolding)
                        </p>
                      </div>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        backgroundColor: '#fbbf24',
                        color: '#0f172a',
                        borderRadius: '9999px',
                        fontSize: '0.7rem',
                        fontWeight: '600'
                      }}>
                        📈
                      </span>
                    </div>
                  ))
                ) : (
                  <p style={{ fontSize: '0.75rem', color: '#94a3b8' }}>All students at healthy pace</p>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Social Learning Pairing */}
      <Card style={{
        backgroundColor: 'rgba(15, 23, 42, 0.6)',
        border: '1px solid rgba(74, 222, 128, 0.3)',
        borderRadius: '0.5rem'
      }}>
        <CardHeader>
          <CardTitle style={{ color: '#4ade80', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            👥 Peer Tutoring Pairing
          </CardTitle>
          <p style={{ color: '#94a3b8', fontSize: '0.75rem', marginTop: '0.5rem' }}>
            Match strong students with those who are struggling on the same concept
          </p>
        </CardHeader>
        <CardContent>
          {pairingOpportunities.length > 0 ? (
            <div style={{ display: 'grid', gap: '1rem', maxHeight: '400px', overflowY: 'auto' }}>
              {pairingOpportunities.map((pairing, idx) => (
                <div key={idx} style={{
                  padding: '1rem',
                  backgroundColor: 'rgba(74, 222, 128, 0.1)',
                  border: '1px solid rgba(74, 222, 128, 0.2)',
                  borderRadius: '0.375rem'
                }}>
                  <p style={{ fontSize: '0.75rem', fontWeight: '600', color: '#4ade80', marginBottom: '0.5rem' }}>
                    📚 {pairing.concept}
                  </p>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                    <div style={{ flex: 1, padding: '0.5rem', backgroundColor: 'rgba(167, 139, 250, 0.2)', borderRadius: '0.25rem' }}>
                      <p style={{ fontSize: '0.7rem', color: '#94a3b8', marginBottom: '0.25rem' }}>MENTOR</p>
                      <p style={{ fontSize: '0.875rem', fontWeight: '600', color: '#f1f5f9' }}>
                        {pairing.mentor.name}
                      </p>
                    </div>
                    <span style={{ color: '#4ade80', fontSize: '1.25rem' }}>→</span>
                    <div style={{ flex: 1, padding: '0.5rem', backgroundColor: 'rgba(250, 204, 21, 0.2)', borderRadius: '0.25rem' }}>
                      <p style={{ fontSize: '0.7rem', color: '#94a3b8', marginBottom: '0.25rem' }}>MENTEE</p>
                      <p style={{ fontSize: '0.875rem', fontWeight: '600', color: '#f1f5f9' }}>
                        {pairing.mentee.name}
                      </p>
                    </div>
                  </div>
                  <button style={{
                    width: '100%',
                    padding: '0.5rem',
                    backgroundColor: '#4ade80',
                    color: '#0f172a',
                    borderRadius: '0.25rem',
                    border: 'none',
                    fontSize: '0.75rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#22c55e'
                    e.currentTarget.style.transform = 'scale(1.02)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = '#4ade80'
                    e.currentTarget.style.transform = 'scale(1)'
                  }}>
                    Suggest Pairing
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ fontSize: '0.875rem', color: '#94a3b8', textAlign: 'center', padding: '1rem' }}>
              ✅ No pairing opportunities at this time
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
