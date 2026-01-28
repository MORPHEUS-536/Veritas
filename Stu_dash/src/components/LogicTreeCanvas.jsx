import { useCallback, useState } from 'react'
import ReactFlow, {
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Background,
  Controls,
  MiniMap,
} from 'reactflow'
import 'reactflow/dist/style.css'

const initialNodes = [
  { id: '1', data: { label: 'Thesis' }, position: { x: 250, y: 0 } },
  { id: '2', data: { label: 'Argument 1' }, position: { x: 100, y: 100 } },
  { id: '3', data: { label: 'Argument 2' }, position: { x: 400, y: 100 } },
  { id: '4', data: { label: 'Evidence A' }, position: { x: 0, y: 200 } },
  { id: '5', data: { label: 'Evidence B' }, position: { x: 200, y: 200 } },
  { id: '6', data: { label: 'Evidence C' }, position: { x: 500, y: 200 } },
]

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2' },
  { id: 'e1-3', source: '1', target: '3' },
  { id: 'e2-4', source: '2', target: '4' },
  { id: 'e2-5', source: '2', target: '5' },
  { id: 'e3-6', source: '3', target: '6' },
]

export default function LogicTreeCanvas() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  const onConnect = useCallback(
    (connection) => setEdges((eds) => addEdge(connection, eds)),
    [setEdges]
  )

  return (
    <div style={{ width: '100%', height: '600px' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  )
}
