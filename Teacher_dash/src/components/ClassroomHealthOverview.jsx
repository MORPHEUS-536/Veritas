import { TrendingUp, TrendingDown, AlertCircle, Zap } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'

export default function ClassroomHealthOverview({ 
  totalStudents, 
  studentsActive, 
  studentsFlagged, 
  studentsHighRisk, 
  averageProgressScore,
  stagnationTrend 
}) {
  const getHealthStatus = () => {
    if (studentsHighRisk > totalStudents * 0.3) return 'AT-RISK'
    if (averageProgressScore > 70) return 'ACCELERATING'
    return 'STABLE'
  }

  const getHealthColor = () => {
    const status = getHealthStatus()
    if (status === 'AT-RISK') return '#ef4444'
    if (status === 'ACCELERATING') return '#4ade80'
    return '#60a5fa'
  }

  const getHealthBg = () => {
    const status = getHealthStatus()
    if (status === 'AT-RISK') return 'rgba(239, 68, 68, 0.1)'
    if (status === 'ACCELERATING') return 'rgba(74, 222, 128, 0.1)'
    return 'rgba(96, 165, 250, 0.1)'
  }

  const healthStatusIcon = {
    'AT-RISK': '⚠️',
    'ACCELERATING': '🚀',
    'STABLE': '⚡'
  }

  return (
    <Card style={{
      backgroundColor: getHealthBg(),
      border: `2px solid ${getHealthColor()}`,
      borderRadius: '0.5rem'
    }}>
      <CardHeader style={{ paddingBottom: '1rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <CardTitle style={{ color: '#f1f5f9', fontSize: '1.25rem', marginBottom: '0.5rem' }}>
              📊 Classroom Health
            </CardTitle>
            <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>
              Real-time cohort analysis
            </p>
          </div>
          <span style={{ fontSize: '1.5rem' }}>{healthStatusIcon[getHealthStatus()]}</span>
        </div>
      </CardHeader>
      <CardContent>
        <div style={{ 
          padding: '1rem',
          backgroundColor: 'rgba(15, 23, 42, 0.5)',
          borderRadius: '0.375rem',
          marginBottom: '1rem',
          border: `1px solid ${getHealthColor()}`
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '1.125rem', fontWeight: '600', color: '#f1f5f9' }}>Status</span>
            <span style={{
              padding: '0.25rem 0.75rem',
              borderRadius: '9999px',
              backgroundColor: getHealthColor(),
              color: '#0f172a',
              fontSize: '0.75rem',
              fontWeight: '600'
            }}>
              {getHealthStatus()}
            </span>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem', marginBottom: '1rem' }}>
          <div style={{
            padding: '0.75rem',
            backgroundColor: 'rgba(30, 41, 59, 0.8)',
            borderRadius: '0.375rem',
            border: '1px solid rgba(71, 85, 105, 0.3)'
          }}>
            <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Active Students</p>
            <p style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#f1f5f9' }}>
              {studentsActive}/{totalStudents}
            </p>
          </div>
          <div style={{
            padding: '0.75rem',
            backgroundColor: 'rgba(30, 41, 59, 0.8)',
            borderRadius: '0.375rem',
            border: '1px solid rgba(71, 85, 105, 0.3)'
          }}>
            <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Avg Progress</p>
            <p style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#60a5fa' }}>
              {averageProgressScore}%
            </p>
          </div>
          <div style={{
            padding: '0.75rem',
            backgroundColor: 'rgba(30, 41, 59, 0.8)',
            borderRadius: '0.375rem',
            border: '1px solid rgba(71, 85, 105, 0.3)'
          }}>
            <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Flagged</p>
            <p style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#fbbf24' }}>
              {studentsFlagged}
            </p>
          </div>
          <div style={{
            padding: '0.75rem',
            backgroundColor: 'rgba(30, 41, 59, 0.8)',
            borderRadius: '0.375rem',
            border: '1px solid rgba(71, 85, 105, 0.3)'
          }}>
            <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.25rem' }}>High Risk</p>
            <p style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#ef4444' }}>
              {studentsHighRisk}
            </p>
          </div>
        </div>

        {stagnationTrend && (
          <div style={{
            padding: '0.75rem',
            backgroundColor: 'rgba(250, 204, 21, 0.1)',
            border: '1px solid rgba(250, 204, 21, 0.3)',
            borderRadius: '0.375rem'
          }}>
            <p style={{ fontSize: '0.75rem', color: '#fbbf24', fontWeight: '600', marginBottom: '0.25rem' }}>
              📍 Stagnation Alert
            </p>
            <p style={{ fontSize: '0.75rem', color: '#fcd34d' }}>
              {stagnationTrend}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
