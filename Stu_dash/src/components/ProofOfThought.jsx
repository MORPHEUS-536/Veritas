export default function ProofOfThought({ score }) {
  const getScoreColor = (score) => {
    if (score >= 80) return '#4ade80'
    if (score >= 60) return '#facc15'
    return '#f87171'
  }

  const getScoreBg = (score) => {
    if (score >= 80) return 'rgba(16, 185, 129, 0.1)'
    if (score >= 60) return 'rgba(251, 146, 60, 0.1)'
    return 'rgba(239, 68, 68, 0.1)'
  }

  const getBorderColor = (score) => {
    if (score >= 80) return 'rgba(16, 185, 129, 0.3)'
    if (score >= 60) return 'rgba(251, 146, 60, 0.3)'
    return 'rgba(239, 68, 68, 0.3)'
  }

  return (
    <div style={{ 
      borderRadius: '0.5rem', 
      border: `1px solid ${getBorderColor(score)}`,
      padding: '1.5rem',
      backgroundColor: getScoreBg(score),
      backdropFilter: 'blur(4px)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#f1f5f9' }}>Proof-of-Thought</h2>
        <span style={{ fontSize: '1.5rem' }}>🎓</span>
      </div>
      
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: '3rem', fontWeight: 'bold', marginBottom: '0.5rem', color: getScoreColor(score) }}>
          {score}%
        </div>
        <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginBottom: '1rem' }}>Academic Integrity Score</p>
        
        <div style={{ width: '100%', backgroundColor: '#1e293b', borderRadius: '9999px', height: '0.5rem', marginBottom: '1rem' }}>
          <div 
            style={{
              height: '0.5rem',
              borderRadius: '9999px',
              transition: 'all 0.5s ease',
              backgroundColor: getScoreColor(score),
              width: `${score}%`
            }}
          ></div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.75rem', color: '#94a3b8' }}>
          <div>
            <p style={{ fontWeight: '600', color: '#cbd5e1' }}>Assessments</p>
            <p>3 of 5</p>
          </div>
          <div>
            <p style={{ fontWeight: '600', color: '#cbd5e1' }}>Submissions</p>
            <p>7 on-time</p>
          </div>
        </div>
      </div>
    </div>
  )
}
