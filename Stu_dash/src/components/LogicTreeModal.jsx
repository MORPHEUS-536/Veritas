import { useState } from 'react'
import LogicTreeCanvas from './LogicTreeCanvas'

export default function LogicTreeModal({ isOpen, onClose }) {
  if (!isOpen) return null

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      backdropFilter: 'blur(4px)',
      zIndex: 50,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1rem'
    }}>
      <div style={{
        backgroundColor: '#1e293b',
        borderRadius: '0.5rem',
        border: '1px solid #334155',
        maxWidth: '56rem',
        width: '100%',
        maxHeight: '90vh',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '1.5rem',
          borderBottom: '1px solid #334155'
        }}>
          <div>
            <h2 style={{ fontSize: '1.875rem', fontWeight: 'bold', color: '#f1f5f9' }}>Logic Tree Canvas</h2>
            <p style={{ fontSize: '0.875rem', color: '#94a3b8', marginTop: '0.25rem' }}>Visualize your logical arguments and reasoning structure</p>
          </div>
          <button
            onClick={onClose}
            style={{
              color: '#94a3b8',
              fontSize: '1.5rem',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              transition: 'color 0.2s'
            }}
            onMouseEnter={(e) => e.target.style.color = '#cbd5e1'}
            onMouseLeave={(e) => e.target.style.color = '#94a3b8'}
          >
            ×
          </button>
        </div>

        {/* Canvas */}
        <div style={{ flex: 1, overflow: 'hidden' }}>
          <LogicTreeCanvas />
        </div>

        {/* Footer */}
        <div style={{
          borderTop: '1px solid #334155',
          padding: '1.5rem',
          display: 'flex',
          gap: '0.75rem',
          justifyContent: 'flex-end',
          backgroundColor: 'rgba(3, 7, 18, 0.5)'
        }}>
          <button
            onClick={onClose}
            style={{
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
            Close
          </button>
          <button style={{
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
            Save Canvas
          </button>
        </div>
      </div>
    </div>
  )
}
