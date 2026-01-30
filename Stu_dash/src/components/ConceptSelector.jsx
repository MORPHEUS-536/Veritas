export default function ConceptSelector({ concepts, onSelectConcept, selectedConceptId }) {
  const difficultyColor = (level) => {
    switch(level) {
      case 1: return '#4ade80'
      case 2: return '#60a5fa'
      case 3: return '#facc15'
      case 4: return '#f97316'
      case 5: return '#ef4444'
      default: return '#94a3b8'
    }
  }

  const difficultyLabel = (level) => {
    const labels = {
      1: 'Intro',
      2: 'Beginner',
      3: 'Intermediate',
      4: 'Advanced',
      5: 'Expert'
    }
    return labels[level] || 'Unknown'
  }

  return (
    <div style={{
      borderRadius: '0.5rem',
      border: '1px solid rgba(71, 85, 105, 0.5)',
      padding: '1.5rem',
      backgroundColor: 'rgba(15, 23, 42, 0.6)',
      backdropFilter: 'blur(4px)',
      marginBottom: '2rem'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#f1f5f9' }}>📚 Select a Concept</h2>
        <span style={{ fontSize: '0.875rem', color: '#94a3b8' }}>{concepts?.length || 0} Available Topics</span>
      </div>

      <div style={{ 
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
        gap: '1rem'
      }}>
        {concepts && concepts.map(concept => (
          <div
            key={concept.concept_id}
            onClick={() => onSelectConcept(concept.concept_id)}
            style={{
              padding: '1rem',
              borderRadius: '0.5rem',
              border: selectedConceptId === concept.concept_id 
                ? '2px solid #a78bfa' 
                : '1px solid rgba(71, 85, 105, 0.3)',
              backgroundColor: selectedConceptId === concept.concept_id
                ? 'rgba(167, 139, 250, 0.1)'
                : 'rgba(30, 41, 59, 0.8)',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: selectedConceptId === concept.concept_id 
                ? '0 0 20px rgba(167, 139, 250, 0.3)'
                : 'none'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = selectedConceptId === concept.concept_id
                ? 'rgba(167, 139, 250, 0.15)'
                : 'rgba(30, 41, 59, 0.95)'
              e.currentTarget.style.borderColor = '#a78bfa'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = selectedConceptId === concept.concept_id
                ? 'rgba(167, 139, 250, 0.1)'
                : 'rgba(30, 41, 59, 0.8)'
              e.currentTarget.style.borderColor = selectedConceptId === concept.concept_id
                ? '2px solid #a78bfa'
                : '1px solid rgba(71, 85, 105, 0.3)'
            }}
          >
            <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#f1f5f9', marginBottom: '0.5rem' }}>
              {concept.concept_name}
            </h3>
            <p style={{ fontSize: '0.875rem', color: '#94a3b8', marginBottom: '0.75rem' }}>
              {concept.subject}
            </p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <span style={{
                display: 'inline-block',
                padding: '0.25rem 0.75rem',
                borderRadius: '9999px',
                backgroundColor: difficultyColor(concept.difficulty_level),
                color: '#0f172a',
                fontSize: '0.75rem',
                fontWeight: '600'
              }}>
                {difficultyLabel(concept.difficulty_level)}
              </span>
            </div>
            <p style={{ fontSize: '0.75rem', color: '#64748b' }}>
              Attempts: <span style={{ fontWeight: '600', color: '#cbd5e1' }}>{concept.attempt_count}</span>
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}
