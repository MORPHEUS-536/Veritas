import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'

/**
 * Main App Component
 * Router setup for the Student Dashboard
 * 
 * Future: Can be extended to include Login Page route
 * import LoginPage from '../Login_Page/src/pages/LoginPage'
 */
export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        {/* Future routes can be added here */}
        {/* <Route path="/login" element={<LoginPage />} /> */}
      </Routes>
    </Router>
  )
}
