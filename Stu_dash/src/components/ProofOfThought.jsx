export default function ProofOfThought({ score }) {
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-400'
    if (score >= 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getScoreBgColor = (score) => {
    if (score >= 80) return 'bg-green-500/10 border-green-500/30'
    if (score >= 60) return 'bg-yellow-500/10 border-yellow-500/30'
    return 'bg-red-500/10 border-red-500/30'
  }

  return (
    <div className={`rounded-lg border p-6 ${getScoreBgColor(score)} backdrop-blur-sm`}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-slate-50">Proof-of-Thought</h2>
        <span className="text-2xl">🎓</span>
      </div>
      
      <div className="text-center">
        <div className={`text-5xl font-bold mb-2 ${getScoreColor(score)}`}>
          {score}%
        </div>
        <p className="text-slate-400 text-sm mb-4">Academic Integrity Score</p>
        
        <div className="w-full bg-slate-800 rounded-full h-2 mb-4">
          <div 
            className={`h-2 rounded-full transition-all duration-500 ${
              score >= 80 ? 'bg-green-400' : score >= 60 ? 'bg-yellow-400' : 'bg-red-400'
            }`}
            style={{ width: `${score}%` }}
          ></div>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs text-slate-400">
          <div>
            <p className="font-semibold text-slate-300">Assessments</p>
            <p>3 of 5</p>
          </div>
          <div>
            <p className="font-semibold text-slate-300">Submissions</p>
            <p>7 on-time</p>
          </div>
        </div>
      </div>
    </div>
  )
}
