import { useRef, useEffect } from 'react'

const ScrollArea = ({ children, className = '' }) => {
  const scrollRef = useRef(null)

  return (
    <div
      ref={scrollRef}
      className={`overflow-y-auto ${className}`}
      style={{
        scrollbarWidth: 'thin',
        scrollbarColor: '#475569 #1e293b'
      }}
    >
      <style>{`
        .scroll-area::-webkit-scrollbar {
          width: 8px;
        }
        .scroll-area::-webkit-scrollbar-track {
          background: #1e293b;
        }
        .scroll-area::-webkit-scrollbar-thumb {
          background: #475569;
          border-radius: 4px;
        }
        .scroll-area::-webkit-scrollbar-thumb:hover {
          background: #64748b;
        }
      `}</style>
      <div className="scroll-area h-full">
        {children}
      </div>
    </div>
  )
}

export default function CurrentAssignment({ assignment }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm overflow-hidden flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-50">{assignment.title}</h2>
          <p className="text-slate-400 text-sm mt-1">{assignment.description}</p>
        </div>
        <span className="text-3xl">📚</span>
      </div>

      <div className="flex-1 min-h-[400px] max-h-[600px]">
        <ScrollArea className="rounded-lg bg-slate-950/50 border border-slate-800">
          <div className="p-6 text-slate-300 whitespace-pre-wrap text-sm leading-relaxed font-mono">
            {assignment.instructions}
          </div>
        </ScrollArea>
      </div>

      <div className="mt-4 flex gap-3">
        <button className="flex-1 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-semibold transition-colors">
          Start Assignment
        </button>
        <button className="flex-1 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg font-semibold transition-colors">
          Ask for Clarification
        </button>
      </div>
    </div>
  )
}
