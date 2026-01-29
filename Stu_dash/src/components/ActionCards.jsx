import { useState } from 'react'
import LogicTreeModal from './LogicTreeModal'

export default function ActionCards({ workstreams, onActionClick, isLoading }) {
  const [logicTreeModalOpen, setLogicTreeModalOpen] = useState(false)
  const [currentWorkstream, setCurrentWorkstream] = useState(null)

  const handleOpenLogicTree = (workstream) => {
    setCurrentWorkstream(workstream)
    setLogicTreeModalOpen(true)
  }

  const getProgressColor = (progress) => {
    if (progress >= 75) return '#10b981'
    if (progress >= 50) return '#3b82f6'
    if (progress >= 25) return '#f59e0b'
    return '#64748b'
  }

  const getStatusColor = (status) => {
    if (status === 'completed') return { bg: 'rgba(16, 185, 129, 0.2)', text: '#6ee7b7', border: 'rgba(16, 185, 129, 0.3)' }
    if (status === 'in-progress') return { bg: 'rgba(59, 130, 246, 0.2)', text: '#93c5fd', border: 'rgba(59, 130, 246, 0.3)' }
    return { bg: 'rgba(71, 85, 105, 0.5)', text: '#cbd5e1', border: '#475569' }
  }

  return (
    <div>
      <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#f1f5f9', marginBottom: '1rem' }}>Work Streams - Thought Evolution</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        {workstreams.map((workstream) => {
          const statusColor = getStatusColor(workstream.status)
          
          return (
            <div
              key={workstream.id}
              style={{
                borderRadius: '0.5rem',
                border: '1px solid #334155',
                backgroundColor: 'rgba(15, 23, 42, 0.5)',
                padding: '1.5rem',
                backdropFilter: 'blur(4px)',
                transition: 'border-color 0.2s'
              }}
              onMouseEnter={(e) => e.currentTarget.style.borderColor = '#475569'}
              onMouseLeave={(e) => e.currentTarget.style.borderColor = '#334155'}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                <div style={{ display: 'flex', gap: '0.75rem', flex: 1 }}>
                  <span style={{ fontSize: '1.875rem' }}>{workstream.icon}</span>
                  <div>
                    <h4 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#f1f5f9' }}>{workstream.name}</h4>
                    <p style={{ fontSize: '0.875rem', color: '#94a3b8' }}>{workstream.description}</p>
                  </div>
                </div>
              </div>

              {/* Status Badge */}
              <div style={{ marginBottom: '1rem' }}>
                <span style={{
                  display: 'inline-block',
                  padding: '0.25rem 0.75rem',
                  borderRadius: '9999px',
                  fontSize: '0.75rem',
                  fontWeight: '500',
                  border: `1px solid ${statusColor.border}`,
                  backgroundColor: statusColor.bg,
                  color: statusColor.text
                }}>
                  {workstream.status === 'completed' ? 'Completed' : workstream.status === 'in-progress' ? 'In Progress' : 'Not Started'}
                </span>
                {workstream.lastUpdated && (
                  <p style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.25rem' }}>Updated {workstream.lastUpdated}</p>
                )}
              </div>

              {/* Progress Bar */}
              <div style={{ marginBottom: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <p style={{ fontSize: '0.75rem', fontWeight: '500', color: '#94a3b8' }}>Progress</p>
                  <span style={{ fontSize: '0.875rem', fontWeight: '600', color: '#cbd5e1' }}>{workstream.progress}%</span>
                </div>
                <div style={{ width: '100%', backgroundColor: '#1e293b', borderRadius: '9999px', height: '0.5rem' }}>
                  <div
                    style={{
                      height: '0.5rem',
                      borderRadius: '9999px',
                      backgroundColor: getProgressColor(workstream.progress),
                      width: `${workstream.progress}%`,
                      transition: 'width 0.5s ease'
                    }}
                  ></div>
                </div>
              </div>

              {/* Thought Evolution Details */}
              <div style={{ backgroundColor: 'rgba(3, 7, 18, 0.5)', borderRadius: '0.5rem', padding: '0.75rem', marginBottom: '1rem', border: '1px solid #334155' }}>
                <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Thought Evolution</p>
                <div style={{ display: 'flex', gap: '0.25rem' }}>
                  {Array.from({ length: 5 }).map((_, i) => (
                    <div
                      key={i}
                      style={{
                        height: '0.5rem',
                        flex: 1,
                        borderRadius: '9999px',
                        backgroundColor: i < Math.ceil(workstream.progress / 20) ? '#8b5cf6' : '#475569'
                      }}
                    ></div>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                {workstream.id === 1 ? (
                  <button
                    onClick={() => handleOpenLogicTree(workstream)}
                    disabled={isLoading}
                    style={{
                      flex: 1,
                      padding: '0.5rem 0.75rem',
                      backgroundColor: '#7c3aed',
                      color: 'white',
                      borderRadius: '0.5rem',
                      fontWeight: '600',
                      border: 'none',
                      cursor: 'pointer',
                      fontSize: '0.875rem',
                      opacity: isLoading ? 0.5 : 1,
                      transition: 'background-color 0.2s'
                    }}
                    onMouseEnter={(e) => !isLoading && (e.target.style.backgroundColor = '#6d28d9')}
                    onMouseLeave={(e) => (e.target.style.backgroundColor = '#7c3aed')}
                  >
                    {isLoading ? 'Opening...' : 'Open Canvas'}
                  </button>
                ) : workstream.status === 'not-started' ? (
                  <button
                    onClick={() => onActionClick(workstream.id, 'start')}
                    disabled={isLoading}
                    style={{
                      flex: 1,
                      padding: '0.5rem 0.75rem',
                      backgroundColor: '#7c3aed',
                      color: 'white',
                      borderRadius: '0.5rem',
                      fontWeight: '600',
                      border: 'none',
                      cursor: 'pointer',
                      fontSize: '0.875rem',
                      opacity: isLoading ? 0.5 : 1,
                      transition: 'background-color 0.2s'
                    }}
                    onMouseEnter={(e) => !isLoading && (e.target.style.backgroundColor = '#6d28d9')}
                    onMouseLeave={(e) => (e.target.style.backgroundColor = '#7c3aed')}
                  >
                    {isLoading ? 'Starting...' : 'Start'}
                  </button>
                ) : (
                  <button
                    onClick={() => onActionClick(workstream.id, 'update')}
                    disabled={isLoading}
                    style={{
                      flex: 1,
                      padding: '0.5rem 0.75rem',
                      backgroundColor: '#7c3aed',
                      color: 'white',
                      borderRadius: '0.5rem',
                      fontWeight: '600',
                      border: 'none',
                      cursor: 'pointer',
                      fontSize: '0.875rem',
                      opacity: isLoading ? 0.5 : 1,
                      transition: 'background-color 0.2s'
                    }}
                    onMouseEnter={(e) => !isLoading && (e.target.style.backgroundColor = '#6d28d9')}
                    onMouseLeave={(e) => (e.target.style.backgroundColor = '#7c3aed')}
                  >
                    {isLoading ? 'Updating...' : 'Update'}
                  </button>
                )}
                <button style={{
                  flex: 1,
                  padding: '0.5rem 0.75rem',
                  backgroundColor: '#1e293b',
                  color: '#cbd5e1',
                  borderRadius: '0.5rem',
                  fontWeight: '600',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  transition: 'background-color 0.2s'
                }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#0f172a'}
                onMouseLeave={(e) => e.target.style.backgroundColor = '#1e293b'}
                >
                  Review
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {/* Logic Tree Modal */}
      <LogicTreeModal 
        isOpen={logicTreeModalOpen} 
        onClose={() => setLogicTreeModalOpen(false)}
      />
    </div>
  )
}
