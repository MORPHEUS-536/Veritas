import { Link } from 'react-router-dom'

export default function Header({ studentName, integrityScore }) {
  return (
    <header className="bg-slate-900 border-b border-slate-800">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="text-2xl font-bold text-primary-500">Veritas</div>
            <div className="hidden sm:block">
              <h1 className="text-xl font-semibold text-slate-50">Student Learning Dashboard</h1>
              <p className="text-sm text-slate-400">Track your academic integrity journey</p>
            </div>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="text-right">
              <p className="text-sm text-slate-400">Welcome back</p>
              <p className="text-lg font-semibold text-slate-50">{studentName}</p>
            </div>
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
              <span className="text-white font-bold">{studentName.charAt(0)}</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
