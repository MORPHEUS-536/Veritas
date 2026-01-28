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
    if (progress >= 75) return 'bg-green-500'
    if (progress >= 50) return 'bg-blue-500'
    if (progress >= 25) return 'bg-yellow-500'
    return 'bg-slate-600'
  }

  const getStatusBadgeColor = (status) => {
    if (status === 'completed') return 'bg-green-500/20 text-green-300 border-green-500/30'
    if (status === 'in-progress') return 'bg-blue-500/20 text-blue-300 border-blue-500/30'
    return 'bg-slate-700/50 text-slate-300 border-slate-700'
  }

  return (
    <div>
      <h3 className="text-xl font-bold text-slate-50 mb-4">Work Streams - Thought Evolution</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {workstreams.map((workstream) => (
          <div
            key={workstream.id}
            className="rounded-lg border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm hover:border-slate-700 transition-colors"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-start gap-3">
                <span className="text-3xl">{workstream.icon}</span>
                <div>
                  <h4 className="text-lg font-semibold text-slate-50">{workstream.name}</h4>
                  <p className="text-sm text-slate-400">{workstream.description}</p>
                </div>
              </div>
            </div>

            {/* Status Badge */}
            <div className="mb-4">
              <span className={`inline-block px-2.5 py-1 rounded-full text-xs font-medium border ${getStatusBadgeColor(workstream.status)}`}>
                {workstream.status === 'completed' ? 'Completed' : workstream.status === 'in-progress' ? 'In Progress' : 'Not Started'}
              </span>
              {workstream.lastUpdated && (
                <p className="text-xs text-slate-500 mt-1">Updated {workstream.lastUpdated}</p>
              )}
            </div>

            {/* Progress Bar */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-medium text-slate-400">Progress</p>
                <span className="text-sm font-semibold text-slate-300">{workstream.progress}%</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-500 ${getProgressColor(workstream.progress)}`}
                  style={{ width: `${workstream.progress}%` }}
                ></div>
              </div>
            </div>

            {/* Thought Evolution Details */}
            <div className="bg-slate-950/50 rounded-lg p-3 mb-4 border border-slate-800">
              <p className="text-xs text-slate-400 mb-1">Thought Evolution</p>
              <div className="flex gap-1">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div
                    key={i}
                    className={`h-2 flex-1 rounded-full ${
                      i < Math.ceil(workstream.progress / 20)
                        ? 'bg-primary-500'
                        : 'bg-slate-700'
                    }`}
                  ></div>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              {workstream.id === 1 ? (
                // Logic Tree Canvas button
                <button
                  onClick={() => handleOpenLogicTree(workstream)}
                  disabled={isLoading}
                  className="flex-1 px-3 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white rounded-lg font-semibold transition-colors text-sm"
                >
                  {isLoading ? 'Opening...' : 'Open Canvas'}
                </button>
              ) : workstream.status === 'not-started' ? (
                <button
                  onClick={() => onActionClick(workstream.id, 'start')}
                  disabled={isLoading}
                  className="flex-1 px-3 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white rounded-lg font-semibold transition-colors text-sm"
                >
                  {isLoading ? 'Starting...' : 'Start'}
                </button>
              ) : (
                <button
                  onClick={() => onActionClick(workstream.id, 'update')}
                  disabled={isLoading}
                  className="flex-1 px-3 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white rounded-lg font-semibold transition-colors text-sm"
                >
                  {isLoading ? 'Updating...' : 'Update'}
                </button>
              )}
              <button className="flex-1 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg font-semibold transition-colors text-sm">
                Review
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Logic Tree Modal */}
      <LogicTreeModal 
        isOpen={logicTreeModalOpen} 
        onClose={() => setLogicTreeModalOpen(false)}
      />
    </div>
  )
}
