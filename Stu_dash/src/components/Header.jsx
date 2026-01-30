export default function Header({ studentName, integrityScore }) {
  return (
    <header style={{ backgroundColor: '#1e293b', borderBottom: '1px solid #334155' }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '1rem 1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#a78bfa' }}>Veritas</div>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#f1f5f9' }}>Student Learning Dashboard</h1>
            <p style={{ fontSize: '0.875rem', color: '#94a3b8' }}>Track your academic integrity journey</p>
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div style={{ textAlign: 'right' }}>
            <p style={{ fontSize: '0.875rem', color: '#94a3b8' }}>Welcome back</p>
            <p style={{ fontSize: '1.125rem', fontWeight: '600', color: '#f1f5f9' }}>{studentName}</p>
          </div>
          <div style={{ width: '2.5rem', height: '2.5rem', borderRadius: '50%', background: 'linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold' }}>
            {studentName?.charAt(0)}
          </div>
        </div>
      </div>
    </header>
  )
}
