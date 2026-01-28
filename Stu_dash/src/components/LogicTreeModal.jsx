import { useState } from 'react'
import LogicTreeCanvas from './LogicTreeCanvas'

export default function LogicTreeModal({ isOpen, onClose }) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 rounded-lg border border-slate-800 max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-800">
          <div>
            <h2 className="text-2xl font-bold text-slate-50">Logic Tree Canvas</h2>
            <p className="text-sm text-slate-400 mt-1">Visualize your logical arguments and reasoning structure</p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 text-2xl transition-colors"
          >
            ×
          </button>
        </div>

        {/* Canvas */}
        <div className="flex-1 overflow-hidden">
          <LogicTreeCanvas />
        </div>

        {/* Footer */}
        <div className="border-t border-slate-800 p-6 flex gap-3 justify-end bg-slate-950/50">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg font-semibold transition-colors"
          >
            Close
          </button>
          <button className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-semibold transition-colors">
            Save Canvas
          </button>
        </div>
      </div>
    </div>
  )
}
