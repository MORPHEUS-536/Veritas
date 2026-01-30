export default function ResponseStrategies({ learningState, currentConcept }) {
  const strategies = {
    PLATEAU: {
      icon: '🎯',
      title: 'The Socratic Pivot',
      description: 'Stop giving direct answers. Ask a high-level conceptual question to break the cycle.',
      action: 'Reflect on the core principles',
      color: '#facc15',
      bgColor: 'rgba(250, 204, 21, 0.1)',
      borderColor: 'rgba(250, 204, 21, 0.3)'
    },
    STALLED: {
      icon: '📚',
      title: 'Scaffolding',
      description: 'Provide a partial solution or a simplified analogy to lower the cognitive barrier.',
      action: 'Break it into smaller steps',
      color: '#f97316',
      bgColor: 'rgba(249, 115, 22, 0.1)',
      borderColor: 'rgba(249, 115, 22, 0.3)'
    },
    PROGRESSING: {
      icon: '🚀',
      title: 'Reinforcement & Challenge',
      description: 'Introduce a "Challenge" variable to push toward the next difficulty level.',
      action: 'Take the next challenge',
      color: '#4ade80',
      bgColor: 'rgba(74, 222, 128, 0.1)',
      borderColor: 'rgba(74, 222, 128, 0.3)'
    }
  }

  const strategy = strategies[learningState] || strategies.PROGRESSING

  return (
    <div style={{
      borderRadius: '0.5rem',
      border: `2px solid ${strategy.borderColor}`,
      padding: '1.5rem',
      backgroundColor: strategy.bgColor,
      backdropFilter: 'blur(4px)',
      marginTop: '2rem'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <span style={{ fontSize: '1.75rem' }}>{strategy.icon}</span>
            <div>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#f1f5f9', margin: 0 }}>
                {strategy.title}
              </h3>
              <p style={{ fontSize: '0.75rem', color: '#94a3b8', margin: '0.25rem 0 0 0' }}>
                Based on your learning state: <span style={{ fontWeight: '600', color: strategy.color }}>{learningState}</span>
              </p>
            </div>
          </div>
          
          <p style={{ fontSize: '0.875rem', color: '#cbd5e1', marginBottom: '1rem', lineHeight: '1.5' }}>
            {strategy.description}
          </p>

          <div style={{
            padding: '0.75rem',
            borderRadius: '0.375rem',
            backgroundColor: 'rgba(0, 0, 0, 0.2)',
            borderLeft: `3px solid ${strategy.color}`
          }}>
            <p style={{ fontSize: '0.75rem', color: '#cbd5e1', margin: 0 }}>
              <span style={{ fontWeight: '600', color: strategy.color }}>💡 Suggestion:</span> {strategy.action}
            </p>
          </div>
        </div>

        <button style={{
          padding: '0.5rem 1rem',
          borderRadius: '0.375rem',
          backgroundColor: strategy.color,
          color: '#0f172a',
          fontSize: '0.75rem',
          fontWeight: '600',
          border: 'none',
          cursor: 'pointer',
          whiteSpace: 'nowrap',
          transition: 'all 0.3s ease'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.opacity = '0.9'
          e.currentTarget.style.transform = 'scale(1.05)'
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.opacity = '1'
          e.currentTarget.style.transform = 'scale(1)'
        }}>
          Get Help
        </button>
      </div>
    </div>
  )
}
