export default function CognitiveAptitude({ data }) {
  return (
    <div style={{ 
      borderRadius: '0.5rem', 
      border: '1px solid #334155',
      backgroundColor: 'rgba(15, 23, 42, 0.5)',
      padding: '1.5rem',
      backdropFilter: 'blur(4px)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#f1f5f9' }}>Cognitive Aptitude Profile</h2>
          <p style={{ fontSize: '0.875rem', color: '#94a3b8' }}>Problem-solving & thinking styles</p>
        </div>
        <span style={{ fontSize: '1.5rem' }}>🧠</span>
      </div>

      {/* Simple bar chart instead of Recharts */}
      <div style={{ marginBottom: '2rem' }}>
        {data.map((item) => (
          <div key={item.name} style={{ marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <p style={{ fontSize: '0.875rem', fontWeight: '600', color: '#cbd5e1' }}>{item.name}</p>
              <p style={{ fontSize: '0.875rem', fontWeight: '600', color: '#a78bfa' }}>{item.value}%</p>
            </div>
            <div style={{ width: '100%', backgroundColor: '#1e293b', borderRadius: '9999px', height: '0.75rem', overflow: 'hidden' }}>
              <div
                style={{
                  height: '0.75rem',
                  borderRadius: '9999px',
                  backgroundColor: '#8b5cf6',
                  width: `${item.value}%`,
                  transition: 'width 0.5s ease'
                }}
              ></div>
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: '1rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))', gap: '0.5rem' }}>
        {data.map((item) => (
          <div key={item.name} style={{ textAlign: 'center', padding: '0.5rem' }}>
            <p style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{item.name}</p>
            <p style={{ fontSize: '0.875rem', fontWeight: '600', color: '#a78bfa' }}>{item.value}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
