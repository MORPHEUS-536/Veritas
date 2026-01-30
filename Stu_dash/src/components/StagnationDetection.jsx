export default function StagnationDetection({ 
  stagnationDurationMinutes, 
  repeatAttemptCount, 
  noProgressFlag, 
  learningState, 
  dropoutRiskLevel 
}) {
  const getStateColor = (state) => {
    switch(state) {
      case 'PROGRESSING': return '#4ade80'
      case 'PLATEAU': return '#facc15'
      case 'STALLED': return '#ef4444'
      default: return '#94a3b8'
    }
  }

  const getStateBg = (state) => {
    switch(state) {
      case 'PROGRESSING': return 'rgba(74, 222, 128, 0.1)'
      case 'PLATEAU': return 'rgba(250, 204, 21, 0.1)'
      case 'STALLED': return 'rgba(239, 68, 68, 0.1)'
      default: return 'rgba(148, 163, 184, 0.1)'
    }
  }

  const getStateBorder = (state) => {
    switch(state) {
      case 'PROGRESSING': return 'rgba(74, 222, 128, 0.3)'
      case 'PLATEAU': return 'rgba(250, 204, 21, 0.3)'
      case 'STALLED': return 'rgba(239, 68, 68, 0.3)'
      default: return 'rgba(148, 163, 184, 0.3)'
    }
  }

  const getRiskColor = (risk) => {
    switch(risk) {
      case 'LOW': return '#4ade80'
      case 'MEDIUM': return '#facc15'
      case 'HIGH': return '#ef4444'
      default: return '#94a3b8'
    }
  }

  const getRiskBg = (risk) => {
    switch(risk) {
      case 'LOW': return 'rgba(74, 222, 128, 0.1)'
      case 'MEDIUM': return 'rgba(250, 204, 21, 0.1)'
      case 'HIGH': return 'rgba(239, 68, 68, 0.1)'
      default: return 'rgba(148, 163, 184, 0.1)'
    }
  }

  const getRiskBorder = (risk) => {
    switch(risk) {
      case 'LOW': return 'rgba(74, 222, 128, 0.3)'
      case 'MEDIUM': return 'rgba(250, 204, 21, 0.3)'
      case 'HIGH': return 'rgba(239, 68, 68, 0.3)'
      default: return 'rgba(148, 163, 184, 0.3)'
    }
  }

  const getStrategyMessage = (state) => {
    switch(state) {
      case 'PLATEAU':
        return '🎯 The Socratic Pivot: Let\'s take a step back. Can you explain the core concept in your own words?'
      case 'STALLED':
        return '📚 Scaffolding: Let\'s break this down into smaller steps. Here\'s a hint to get you started.'
      case 'PROGRESSING':
        return '🚀 Reinforcement: You\'re doing great! Ready for the next challenge?'
      default:
        return 'Keep working at your own pace. You\'ve got this!'
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
        <h2 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#f1f5f9' }}>⚡ Progress Tracking</h2>
        <span style={{ fontSize: '1.5rem' }}>📊</span>
      </div>

      {/* Stagnation Duration */}
      <div style={{ 
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '1rem',
        marginBottom: '1.5rem'
      }}>
        <div style={{
          padding: '1rem',
          borderRadius: '0.5rem',
          backgroundColor: 'rgba(30, 41, 59, 0.8)',
          border: '1px solid rgba(71, 85, 105, 0.3)'
        }}>
          <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.5rem' }}>Time on Current Step</p>
          <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#f1f5f9' }}>
            {stagnationDurationMinutes || 0}<span style={{ fontSize: '0.875rem', color: '#64748b' }}>m</span>
          </p>
        </div>
        <div style={{
          padding: '1rem',
          borderRadius: '0.5rem',
          backgroundColor: 'rgba(30, 41, 59, 0.8)',
          border: '1px solid rgba(71, 85, 105, 0.3)'
        }}>
          <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.5rem' }}>Repeated Attempts</p>
          <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#f1f5f9' }}>
            {repeatAttemptCount || 0}
          </p>
        </div>
      </div>

      {/* No Progress Flag Alert */}
      {noProgressFlag && (
        <div style={{
          padding: '1rem',
          borderRadius: '0.5rem',
          backgroundColor: 'rgba(250, 204, 21, 0.1)',
          border: '1px solid rgba(250, 204, 21, 0.5)',
          marginBottom: '1rem',
          display: 'flex',
          gap: '0.75rem'
        }}>
          <span style={{ fontSize: '1.25rem' }}>📍</span>
          <div>
            <p style={{ fontSize: '0.875rem', color: '#fbbf24', fontWeight: '600', marginBottom: '0.25rem' }}>
              No Progress Detected
            </p>
            <p style={{ fontSize: '0.75rem', color: '#fcd34d' }}>
              Your scores haven't changed in 3+ interactions. Consider trying a different approach.
            </p>
          </div>
        </div>
      )}

      {/* Learning State */}
      <div style={{
        padding: '1rem',
        borderRadius: '0.5rem',
        backgroundColor: getStateBg(learningState),
        border: `1px solid ${getStateBorder(learningState)}`,
        marginBottom: '1rem'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
          <label style={{ fontSize: '0.875rem', color: '#cbd5e1', fontWeight: '500' }}>Learning State</label>
          <span style={{
            padding: '0.25rem 0.75rem',
            borderRadius: '9999px',
            backgroundColor: getStateColor(learningState),
            color: '#0f172a',
            fontSize: '0.75rem',
            fontWeight: '600'
          }}>
            {learningState || 'PROGRESSING'}
          </span>
        </div>
        <p style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
          {getStrategyMessage(learningState)}
        </p>
      </div>

      {/* Dropout Risk */}
      <div style={{
        padding: '1rem',
        borderRadius: '0.5rem',
        backgroundColor: getRiskBg(dropoutRiskLevel),
        border: `1px solid ${getRiskBorder(dropoutRiskLevel)}`
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
          <label style={{ fontSize: '0.875rem', color: '#cbd5e1', fontWeight: '500' }}>Engagement Risk</label>
          <span style={{
            padding: '0.25rem 0.75rem',
            borderRadius: '9999px',
            backgroundColor: getRiskColor(dropoutRiskLevel),
            color: '#0f172a',
            fontSize: '0.75rem',
            fontWeight: '600'
          }}>
            {dropoutRiskLevel || 'LOW'}
          </span>
        </div>
        {dropoutRiskLevel === 'HIGH' && (
          <div style={{ marginTop: '0.5rem', padding: '0.75rem', backgroundColor: 'rgba(0, 0, 0, 0.2)', borderRadius: '0.375rem' }}>
            <p style={{ fontSize: '0.75rem', color: '#fca5a5', marginBottom: '0.5rem' }}>💡 This is a tough one, don't sweat it.</p>
            <p style={{ fontSize: '0.75rem', color: '#fca5a5', marginBottom: '0.5rem' }}>Consider taking a 5-minute break, then continue refreshed.</p>
            <p style={{ fontSize: '0.75rem', color: '#fca5a5' }}>Or switch to a related concept to build confidence.</p>
          </div>
        )}
      </div>
    </div>
  )
}
