import { useState } from 'react'

export default function LogicTreeCanvas() {
  const [nodes] = useState([
    { id: '1', label: 'Thesis', x: 250, y: 30 },
    { id: '2', label: 'Argument 1', x: 100, y: 120 },
    { id: '3', label: 'Argument 2', x: 400, y: 120 },
    { id: '4', label: 'Evidence A', x: 50, y: 220 },
    { id: '5', label: 'Evidence B', x: 150, y: 220 },
    { id: '6', label: 'Evidence C', x: 450, y: 220 },
  ])

  const edges = [
    { from: 1, to: 2 },
    { from: 1, to: 3 },
    { from: 2, to: 4 },
    { from: 2, to: 5 },
    { from: 3, to: 6 },
  ]

  // Function to draw lines between nodes
  const renderCanvas = () => {
    return (
      <svg style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}>
        {edges.map((edge, idx) => {
          const fromNode = nodes.find(n => n.id === String(edge.from))
          const toNode = nodes.find(n => n.id === String(edge.to))
          return (
            <line
              key={idx}
              x1={fromNode.x + 50}
              y1={fromNode.y + 25}
              x2={toNode.x + 50}
              y2={toNode.y}
              stroke="#8b5cf6"
              strokeWidth="2"
            />
          )
        })}
      </svg>
    )
  }

  return (
    <div style={{ 
      width: '100%', 
      height: '600px',
      backgroundColor: '#0f172a',
      position: 'relative',
      overflow: 'auto',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Canvas SVG for lines */}
      {renderCanvas()}

      {/* Nodes */}
      {nodes.map(node => (
        <div
          key={node.id}
          style={{
            position: 'absolute',
            left: `${node.x}px`,
            top: `${node.y}px`,
            width: '100px',
            height: '50px',
            backgroundColor: '#1e293b',
            border: '2px solid #8b5cf6',
            borderRadius: '0.5rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#f1f5f9',
            fontWeight: '600',
            fontSize: '0.875rem',
            cursor: 'move',
            textAlign: 'center',
            padding: '0.5rem',
            boxSizing: 'border-box'
          }}
        >
          {node.label}
        </div>
      ))}

      {/* Instructions */}
      <div style={{
        position: 'fixed',
        bottom: '1rem',
        right: '1rem',
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        border: '1px solid #334155',
        borderRadius: '0.5rem',
        padding: '1rem',
        maxWidth: '300px',
        color: '#cbd5e1',
        fontSize: '0.875rem'
      }}>
        <p style={{ fontWeight: '600', color: '#f1f5f9', marginBottom: '0.5rem' }}>Logic Tree Canvas</p>
        <p>Drag nodes to reorganize your argument structure. Connect ideas to build your logical framework.</p>
      </div>
    </div>
  )
}
