import { useState } from 'react'

export default function CurrentAssignment({ assignment, concepts, selectedConceptId, onSelectConcept }) {
  const [expandedSubject, setExpandedSubject] = useState(null)

  // Get unique subjects and organize concepts by subject
  const subjectMap = concepts ? concepts.reduce((acc, concept) => {
    if (!acc[concept.subject]) {
      acc[concept.subject] = []
    }
    acc[concept.subject].push(concept)
    return acc
  }, {}) : {}

  const subjects = Object.keys(subjectMap).sort()

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
      border: '1px solid #334155',
      backgroundColor: 'rgba(15, 23, 42, 0.5)',
      padding: '1.5rem',
      backdropFilter: 'blur(4px)',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      marginBottom: '2rem'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
        <div style={{ flex: 1 }}>
          <h2 style={{ fontSize: '1.875rem', fontWeight: 'bold', color: '#f1f5f9' }}>{assignment.title}</h2>
          <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginTop: '0.25rem' }}>{assignment.description}</p>
        </div>
        <span style={{ fontSize: '2rem' }}>📚</span>
      </div>

      {/* Concept Selection Section */}
      {concepts && concepts.length > 0 && (
        <div style={{ 
          marginBottom: '1.5rem', 
          padding: '1rem', 
          borderRadius: '0.5rem',
          backgroundColor: 'rgba(30, 41, 59, 0.5)',
          border: '1px solid rgba(71, 85, 105, 0.3)'
        }}>
          <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#f1f5f9', marginBottom: '1rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <span>📚</span> Select a Concept
          </h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
            {subjects.map(subject => (
              <div key={subject} style={{
                borderRadius: '0.5rem',
                backgroundColor: 'rgba(15, 23, 42, 0.8)',
                border: '1px solid rgba(71, 85, 105, 0.3)'
              }}>
                <button
                  onClick={() => setExpandedSubject(expandedSubject === subject ? null : subject)}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    backgroundColor: 'transparent',
                    color: '#f1f5f9',
                    border: 'none',
                    borderRadius: '0.5rem',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    fontSize: '0.875rem',
                    fontWeight: '600',
                    transition: 'all 0.3s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'rgba(167, 139, 250, 0.1)'
                    e.currentTarget.style.color = '#a78bfa'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent'
                    e.currentTarget.style.color = '#f1f5f9'
                  }}
                >
                  <span>{subject}</span>
                  <span style={{ fontSize: '0.75rem' }}>{expandedSubject === subject ? '▼' : '▶'}</span>
                </button>

                {expandedSubject === subject && (
                  <div style={{
                    borderTop: '1px solid rgba(71, 85, 105, 0.3)',
                    padding: '0.5rem 0'
                  }}>
                    {subjectMap[subject].map(concept => (
                      <button
                        key={concept.concept_id}
                        onClick={() => onSelectConcept(concept.concept_id)}
                        style={{
                          width: '100%',
                          padding: '0.75rem',
                          backgroundColor: selectedConceptId === concept.concept_id 
                            ? 'rgba(167, 139, 250, 0.2)'
                            : 'transparent',
                          color: selectedConceptId === concept.concept_id 
                            ? '#a78bfa'
                            : '#cbd5e1',
                          border: 'none',
                          cursor: 'pointer',
                          fontSize: '0.75rem',
                          textAlign: 'left',
                          paddingLeft: '1.5rem',
                          transition: 'all 0.2s ease',
                          borderLeft: selectedConceptId === concept.concept_id 
                            ? '3px solid #a78bfa'
                            : 'none'
                        }}
                        onMouseEnter={(e) => {
                          if (selectedConceptId !== concept.concept_id) {
                            e.currentTarget.style.backgroundColor = 'rgba(71, 85, 105, 0.2)'
                            e.currentTarget.style.color = '#f1f5f9'
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (selectedConceptId !== concept.concept_id) {
                            e.currentTarget.style.backgroundColor = 'transparent'
                            e.currentTarget.style.color = '#cbd5e1'
                          }
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span>{concept.concept_name}</span>
                          <span style={{
                            display: 'inline-block',
                            padding: '0.125rem 0.5rem',
                            borderRadius: '9999px',
                            backgroundColor: difficultyColor(concept.difficulty_level),
                            color: '#0f172a',
                            fontSize: '0.7rem',
                            fontWeight: '600'
                          }}>
                            {difficultyLabel(concept.difficulty_level)}
                          </span>
                        </div>
                        <p style={{ fontSize: '0.65rem', color: '#64748b', marginTop: '0.25rem' }}>
                          Attempts: {concept.attempt_count}
                        </p>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {assignment.instructions && (
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
      )}

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
