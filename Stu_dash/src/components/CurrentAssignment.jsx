export default function CurrentAssignment({ assignment }) {
  return (
    <div style={{ 
      borderRadius: '0.5rem', 
      border: '1px solid #334155',
      backgroundColor: 'rgba(15, 23, 42, 0.5)',
      padding: '1.5rem',
      backdropFilter: 'blur(4px)',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
        <div style={{ flex: 1 }}>
          <h2 style={{ fontSize: '1.875rem', fontWeight: 'bold', color: '#f1f5f9' }}>{assignment.title}</h2>
          <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginTop: '0.25rem' }}>{assignment.description}</p>
        </div>
        <span style={{ fontSize: '2rem' }}>📚</span>
      </div>

      <div style={{ flex: 1, minHeight: '400px', maxHeight: '600px' }}>
        <div style={{ 
          borderRadius: '0.5rem', 
          backgroundColor: 'rgba(3, 7, 18, 0.5)',
          border: '1px solid #334155',
          overflowY: 'auto',
          padding: '1.5rem'
        }}>
          <div style={{ color: '#cbd5e1', whiteSpace: 'pre-wrap', fontSize: '0.875rem', lineHeight: '1.5', fontFamily: 'monospace' }}>
            {assignment.instructions}
          </div>
        </div>
      </div>

      <div style={{ marginTop: '1rem', display: 'flex', gap: '0.75rem' }}>
        <button style={{ 
          flex: 1, 
          padding: '0.5rem 1rem',
          backgroundColor: '#7c3aed',
          color: 'white',
          borderRadius: '0.5rem',
          fontWeight: '600',
          border: 'none',
          cursor: 'pointer',
          transition: 'background-color 0.2s'
        }}
        onMouseEnter={(e) => e.target.style.backgroundColor = '#6d28d9'}
        onMouseLeave={(e) => e.target.style.backgroundColor = '#7c3aed'}
        >
          Start Assignment
        </button>
        <button style={{ 
          flex: 1, 
          padding: '0.5rem 1rem',
          backgroundColor: '#1e293b',
          color: '#cbd5e1',
          borderRadius: '0.5rem',
          fontWeight: '600',
          border: 'none',
          cursor: 'pointer',
          transition: 'background-color 0.2s'
        }}
        onMouseEnter={(e) => e.target.style.backgroundColor = '#0f172a'}
        onMouseLeave={(e) => e.target.style.backgroundColor = '#1e293b'}
        >
          Ask for Clarification
        </button>
      </div>
    </div>
  )
}
