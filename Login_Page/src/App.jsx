import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './components/LoginPage'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        {/* Dashboard route - will redirect to external Stu_dash app */}
        <Route path="/dashboard" element={<Navigate to="http://localhost:5173" replace />} />
      </Routes>
    </Router>
  )
}

export default App
