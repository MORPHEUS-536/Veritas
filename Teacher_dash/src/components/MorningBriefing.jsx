import { Card, CardContent, CardHeader, CardTitle } from './ui/card'

export default function MorningBriefing({ 
  classroomHealth,
  topStickingPoint,
  integrityAlerts,
  peerDynamics,
  recommendedIntervention 
}) {
  const briefingMessages = {
    'AT-RISK': '🚨 Your classroom needs attention. Review the intervention suggestions below.',
    'STABLE': '✅ Class is on track. Monitor students flagged for review.',
    'ACCELERATING': '🎯 Great progress! Challenge ahead-of-pace students with advanced topics.'
  }

  return (
    <Card style={{
      backgroundColor: 'rgba(15, 23, 42, 0.6)',
      border: '1px solid rgba(167, 139, 250, 0.3)',
      borderRadius: '0.5rem'
    }}>
      <CardHeader>
        <CardTitle style={{ color: '#a78bfa', fontSize: '1.125rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          ☀️ Morning Briefing
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div style={{ marginBottom: '1rem', padding: '1rem', backgroundColor: 'rgba(167, 139, 250, 0.1)', borderRadius: '0.375rem', border: '1px solid rgba(167, 139, 250, 0.2)' }}>
          <p style={{ color: '#cbd5e1', fontSize: '0.875rem', lineHeight: '1.5' }}>
            {briefingMessages[classroomHealth] || briefingMessages['STABLE']}
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem', marginBottom: '1rem' }}>
          <div style={{ padding: '0.75rem', backgroundColor: 'rgba(30, 41, 59, 0.8)', borderRadius: '0.375rem', border: '1px solid rgba(71, 85, 105, 0.3)' }}>
            <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.25rem', fontWeight: '600' }}>Top Sticking Point</p>
            <p style={{ fontSize: '0.875rem', color: '#f1f5f9' }}>{topStickingPoint || 'None identified'}</p>
          </div>
          <div style={{ padding: '0.75rem', backgroundColor: 'rgba(30, 41, 59, 0.8)', borderRadius: '0.375rem', border: '1px solid rgba(71, 85, 105, 0.3)' }}>
            <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.25rem', fontWeight: '600' }}>Integrity Alerts</p>
            <p style={{ fontSize: '0.875rem', color: '#f1f5f9' }}>{integrityAlerts} students</p>
          </div>
          <div style={{ padding: '0.75rem', backgroundColor: 'rgba(30, 41, 59, 0.8)', borderRadius: '0.375rem', border: '1px solid rgba(71, 85, 105, 0.3)' }}>
            <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.25rem', fontWeight: '600' }}>Peer Dynamics</p>
            <p style={{ fontSize: '0.875rem', color: '#f1f5f9' }}>{peerDynamics || 'Balanced'}</p>
          </div>
          <div style={{ padding: '0.75rem', backgroundColor: 'rgba(30, 41, 59, 0.8)', borderRadius: '0.375rem', border: '1px solid rgba(71, 85, 105, 0.3)' }}>
            <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.25rem', fontWeight: '600' }}>Class Pulse</p>
            <p style={{ fontSize: '0.875rem', color: '#4ade80', fontWeight: '600' }}>Active</p>
          </div>
        </div>

        {recommendedIntervention && (
          <div style={{ padding: '1rem', backgroundColor: 'rgba(74, 222, 128, 0.1)', borderRadius: '0.375rem', border: '1px solid rgba(74, 222, 128, 0.3)' }}>
            <p style={{ fontSize: '0.75rem', color: '#4ade80', fontWeight: '600', marginBottom: '0.5rem' }}>
              💡 Recommended Intervention
            </p>
            <p style={{ fontSize: '0.875rem', color: '#cbd5e1' }}>
              {recommendedIntervention}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
