export default function ProgressAndReasoning({ learningProgress, semanticChange, reasoningContinuity }) {
  const getReasoningColor = (continuity) => {
    switch(continuity) {
      case 'HIGH': return '#4ade80'
      case 'MEDIUM': return '#facc15'
      case 'LOW': return '#ef4444'
      default: return '#94a3b8'
    }
  }

  const getReasoningBg = (continuity) => {
    switch(continuity) {
      case 'HIGH': return 'rgba(74, 222, 128, 0.1)'
      case 'MEDIUM': return 'rgba(250, 204, 21, 0.1)'
      case 'LOW': return 'rgba(239, 68, 68, 0.1)'
      default: return 'rgba(148, 163, 184, 0.1)'
    }
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
        <h2 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#f1f5f9' }}>📈 Progress & Reasoning</h2>
        <span style={{ fontSize: '1.5rem' }}>🧠</span>
      </div>

      {/* Learning Progress */}
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
          <label style={{ fontSize: '0.875rem', color: '#cbd5e1', fontWeight: '500' }}>Learning Progress</label>
          <span style={{ fontSize: '0.875rem', color: '#f1f5f9', fontWeight: '600' }}>{learningProgress || 0}%</span>
        </div>
        <div style={{ width: '100%', backgroundColor: '#1e293b', borderRadius: '9999px', height: '0.5rem', overflow: 'hidden' }}>
          <div 
            style={{
              height: '0.5rem',
              borderRadius: '9999px',
              transition: 'width 0.5s ease',
              background: 'linear-gradient(90deg, #60a5fa 0%, #a78bfa 100%)',
              width: `${learningProgress || 0}%`
            }}
          ></div>
        </div>
      </div>

      {/* Semantic Change Score */}
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
          <label style={{ fontSize: '0.875rem', color: '#cbd5e1', fontWeight: '500' }}>Semantic Change Score</label>
          <span style={{ fontSize: '0.875rem', color: '#f1f5f9', fontWeight: '600' }}>{(semanticChange || 0).toFixed(2)}</span>
        </div>
        <div style={{ width: '100%', backgroundColor: '#1e293b', borderRadius: '9999px', height: '0.5rem', overflow: 'hidden' }}>
          <div 
            style={{
              height: '0.5rem',
              borderRadius: '9999px',
              transition: 'width 0.5s ease',
              background: 'linear-gradient(90deg, #06b6d4 0%, #06f 100%)',
              width: `${(semanticChange || 0) * 100}%`
            }}
          ></div>
        </div>
        <p style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.25rem' }}>
          How much your understanding is evolving (0.0 - 1.0)
        </p>
      </div>

      {/* Reasoning Continuity */}
      <div style={{
        padding: '1rem',
        borderRadius: '0.5rem',
        backgroundColor: getReasoningBg(reasoningContinuity),
        border: `1px solid ${getReasoningColor(reasoningContinuity)}`
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <label style={{ fontSize: '0.875rem', color: '#cbd5e1', fontWeight: '500' }}>Reasoning Continuity</label>
          <span style={{
            padding: '0.25rem 0.75rem',
            borderRadius: '9999px',
            backgroundColor: getReasoningColor(reasoningContinuity),
            color: '#0f172a',
            fontSize: '0.75rem',
            fontWeight: '600'
          }}>
            {reasoningContinuity || 'MEDIUM'}
          </span>
        </div>
        <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
          Logical flow between your responses
        </p>
      </div>
    </div>
  )
}
