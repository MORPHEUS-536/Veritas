import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer } from 'recharts'

export default function CognitiveAptitude({ data }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-slate-50">Cognitive Aptitude Profile</h2>
          <p className="text-sm text-slate-400">Problem-solving & thinking styles</p>
        </div>
        <span className="text-2xl">🧠</span>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <RadarChart data={data}>
          <PolarGrid stroke="#1e293b" />
          <PolarAngleAxis dataKey="name" stroke="#94a3b8" style={{ fontSize: '12px' }} />
          <PolarRadiusAxis angle={90} domain={[0, 100]} stroke="#64748b" />
          <Radar 
            name="Cognitive Score" 
            dataKey="value" 
            stroke="#8b5cf6" 
            fill="#8b5cf6" 
            fillOpacity={0.6}
            animationDuration={800}
          />
        </RadarChart>
      </ResponsiveContainer>

      <div className="mt-4 grid grid-cols-2 sm:grid-cols-5 gap-2">
        {data.map((item) => (
          <div key={item.name} className="text-center">
            <p className="text-xs text-slate-400">{item.name}</p>
            <p className="text-sm font-semibold text-primary-400">{item.value}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
