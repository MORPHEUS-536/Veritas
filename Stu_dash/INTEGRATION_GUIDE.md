# Student Dashboard - Integration Guide

## Overview
The Student Dashboard is a comprehensive learning platform that tracks student progress, integrity scores, and cognitive development through multiple work streams.

## Features Implemented

### 1. **Proof-of-Thought Metric Card** ✅
- Displays integrity score (85% by default)
- Visual progress indicator
- Assessment and submission tracking
- Dynamic color coding based on score ranges

### 2. **Cognitive Aptitude Radar Chart** ✅
- Visualizes problem-solving styles
- 5-dimensional analysis:
  - Analytical thinking
  - Creative reasoning
  - Critical analysis
  - Synthesis ability
  - Evaluation skills

### 3. **Current Assignment Section** ✅
- ScrollArea component for detailed instructions
- Teacher-provided assignment details
- Clean typography and formatting
- Start Assignment & Ask for Clarification buttons

### 4. **Work Streams with Progress Tracking** ✅

#### Logic Tree Canvas (🌳)
- Interactive canvas using React Flow
- Visual argument structure mapping
- Node-edge based logical relationships
- Modal interface with save functionality

#### Voice Reflections (🎙️)
- Status tracking for audio recordings
- Progress bar visualization
- Update mechanism for adding reflections

#### Draft History (📝)
- Draft version tracking
- Progress visualization
- Update history timeline

### 5. **Database Integration** ✅
- Local storage implementation (ready for backend API)
- Integrity score persistence
- Workstream update tracking
- Action logging for audit trail
- Timestamp recording for all activities

### 6. **Dark Mode Design** ✅
- Tailwind CSS with dark color scheme
- Slate-950 base with primary-600 accents
- Green success indicators
- Smooth transitions and hover effects

## File Structure

```
src/
├── components/
│   ├── Header.jsx                 # Navigation and student info
│   ├── ProofOfThought.jsx         # Integrity score card
│   ├── CognitiveAptitude.jsx      # Radar chart visualization
│   ├── CurrentAssignment.jsx      # Assignment details with ScrollArea
│   ├── ActionCards.jsx            # Work stream cards
│   ├── LogicTreeCanvas.jsx        # React Flow integration
│   └── LogicTreeModal.jsx         # Modal for Logic Tree
├── pages/
│   └── Dashboard.jsx              # Main page component
├── services/
│   └── DatabaseService.js         # Database operations
├── hooks/
│   └── useIntegrityTracking.js    # Custom tracking hook
├── App.jsx                        # Router setup
├── main.jsx                       # Entry point
└── index.css                      # Global styles
```

## Database Service Methods

### `updateIntegrityScore(studentId, newScore)`
Updates the student's integrity score in the database.

```javascript
await dbService.updateIntegrityScore('student_001', 87)
```

### `recordWorkstreamUpdate(studentId, workstreamId, data)`
Records progress and status updates for work streams.

```javascript
await dbService.recordWorkstreamUpdate('student_001', 1, {
  progress: 60,
  status: 'in-progress'
})
```

### `logAction(studentId, action, metadata)`
Logs all student actions for audit trails.

```javascript
await dbService.logAction('student_001', 'workstream_start', {
  workstreamId: 1,
  timestamp: new Date().toISOString()
})
```

### `getStudentData(studentId)`
Retrieves all stored student data.

```javascript
const { data } = await dbService.getStudentData('student_001')
```

## Integration with Login Page

### Step 1: Add Navigation Link
In `Login_Page/src/pages/LoginPage.jsx`, add navigation after successful login:

```javascript
import { useNavigate } from 'react-router-dom'

const navigate = useNavigate()

// After successful login
navigate('/dashboard', { state: { studentId: 'student_001' } })
```

### Step 2: Set Up Parent Router
Create a root `App.jsx` that combines both routes:

```javascript
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import LoginPage from './Login_Page/src/pages/LoginPage'
import Dashboard from './Stu_dash/src/pages/Dashboard'

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  )
}
```

### Step 3: Pass Student ID from Login
Modify Dashboard to accept student data from router state:

```javascript
import { useLocation } from 'react-router-dom'

export default function Dashboard() {
  const location = useLocation()
  const studentId = location.state?.studentId || 'student_001'
  
  // Use studentId for all database operations
}
```

## API Integration (Future Backend)

Replace localStorage with API calls:

```javascript
// Example: Update integrity score via API
const response = await fetch(
  `${process.env.REACT_APP_API_URL}/students/${studentId}/integrity-score`,
  {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ score: newScore })
  }
)
```

## Customization

### Modify Integrity Score Calculation
In `pages/Dashboard.jsx`, update the score calculation logic:

```javascript
const newScore = Math.min(
  baseScore + (completedWorkstreams * weightFactor),
  100
)
```

### Add New Work Streams
Add to the initial state in `Dashboard.jsx`:

```javascript
{
  id: 4,
  name: 'Peer Collaboration',
  icon: '👥',
  description: 'Engage with classmates',
  progress: 0,
  status: 'not-started',
  lastUpdated: null
}
```

### Customize Cognitive Profile
Update the cognitive dimensions in `Dashboard.jsx`:

```javascript
cognitiveProfile: [
  { name: 'Your Dimension 1', value: 85 },
  // Add more dimensions as needed
]
```

## Running the Application

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Browser Support
- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance Notes
- React Flow canvas optimized for up to 1000 nodes
- Local storage limited to ~5-10MB per domain
- Consider pagination for large action logs

## Future Enhancements
1. Real-time collaboration on Logic Tree Canvas
2. AI-powered cognitive profile analysis
3. Advanced voice reflection transcription
4. Peer feedback integration
5. Export functionality (PDF, JSON)
6. Mobile responsive improvements
