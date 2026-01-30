export default function IntegrityPanel({ integrityScore, suddenJumpFlag, integrityStatusLabel }) {
  const getStatusColor = (status) => {
    switch(status) {
      case 'CONSISTENT': return '#4ade80'
      case 'NEEDS_REVIEW': return '#ef4444'
      default: return '#facc15'
    }
  }

  const getStatusBg = (status) => {
    switch(status) {
      case 'CONSISTENT': return 'rgba(74, 222, 128, 0.1)'
      case 'NEEDS_REVIEW': return 'rgba(239, 68, 68, 0.1)'
      default: return 'rgba(250, 204, 21, 0.1)'
    }
  }

  const getStatusBorder = (status) => {
    switch(status) {
      case 'CONSISTENT': return 'rgba(74, 222, 128, 0.3)'
      case 'NEEDS_REVIEW': return 'rgba(239, 68, 68, 0.3)'
      default: return 'rgba(250, 204, 21, 0.3)'
    }
  }

  const getScoreColor = (score) => {
    if (score >= 0.8) return '#4ade80'
    if (score >= 0.6) return '#facc15'
    return '#ef4444'
  }

  return (
    <div style={{
      borderRadius: '0.5rem',
      border: '1px solid rgba(71, 85, 105, 0.5)',
      padding: '1.5rem',
      backgroundColor: 'rgba(15, 23, 42, 0.6)',
      backdropFilter: 'blur(4px)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#f1f5f9' }}>🛡️ Integrity & Authenticity</h2>
        <span style={{ fontSize: '1.5rem' }}>✓</span>
      </div>

      {/* Integrity Score */}
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <label style={{ fontSize: '0.875rem', color: '#cbd5e1', fontWeight: '500' }}>Integrity Score</label>
          <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: getScoreColor(integrityScore) }}>
            {(integrityScore || 0).toFixed(2)}
          </span>
        </div>
        <div style={{ width: '100%', backgroundColor: '#1e293b', borderRadius: '9999px', height: '0.75rem', overflow: 'hidden' }}>
          <div 
            style={{
              height: '0.75rem',
              borderRadius: '9999px',
              transition: 'all 0.5s ease',
              background: `linear-gradient(90deg, ${getScoreColor(integrityScore)} 0%, #a78bfa 100%)`,
              width: `${(integrityScore || 0) * 100}%`
            }}
          ></div>
        </div>
      </div>

      {/* Sudden Jump Alert */}
      {suddenJumpFlag && (
        <div style={{
          padding: '1rem',
          borderRadius: '0.5rem',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.5)',
          marginBottom: '1rem',
          display: 'flex',
          gap: '0.75rem'
        }}>
          <span style={{ fontSize: '1.25rem' }}>⚠️</span>
          <div>
            <p style={{ fontSize: '0.875rem', color: '#f87171', fontWeight: '600', marginBottom: '0.25rem' }}>
              Sudden Jump Detected
            </p>
            <p style={{ fontSize: '0.75rem', color: '#fca5a5' }}>
              Your mastery increased rapidly. Can you explain the key concepts you've learned?
            </p>
          </div>
        </div>
      )}

      {/* Integrity Status */}
      <div style={{
        padding: '1rem',
        borderRadius: '0.5rem',
        backgroundColor: getStatusBg(integrityStatusLabel),
        border: `1px solid ${getStatusBorder(integrityStatusLabel)}`
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <label style={{ fontSize: '0.875rem', color: '#cbd5e1', fontWeight: '500' }}>Status</label>
          <span style={{
            padding: '0.25rem 0.75rem',
            borderRadius: '9999px',
            backgroundColor: getStatusColor(integrityStatusLabel),
            color: '#0f172a',
            fontSize: '0.75rem',
            fontWeight: '600'
          }}>
            {integrityStatusLabel || 'CONSISTENT'}
          </span>
        </div>
        <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.5rem' }}>
          {integrityStatusLabel === 'NEEDS_REVIEW' 
            ? 'Your work is authentic and genuine. Keep it up!'
            : 'We notice some patterns worth discussing. Focus on understanding, not just answers.'}
        </p>
      </div>
    </div>
  )
}
