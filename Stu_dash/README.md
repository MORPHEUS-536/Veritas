# Student Dashboard - Veritas

A modern, dark-mode centric React-based student dashboard focusing on learning journeys and academic integrity.

## Features

- **Proof-of-Thought Metric Card**: Display 85% integrity score with visual progress
- **Cognitive Aptitude Radar Chart**: Visualize problem-solving styles and thinking patterns
- **Current Assignment Section**: ScrollArea with detailed teacher instructions
- **Work Streams with Progress Tracking**:
  - Logic Tree Canvas
  - Voice Reflections
  - Draft History
  - Thought Evolution progress bars
- **Dark Mode Design**: Modern, sleek interface optimized for dark theme
- **Database Integration**: Tracks integrity scores and work stream updates
- **Action Buttons**: Start/Update buttons for each work stream with integrity score updates

## Installation

```bash
npm install
npm run dev
```

## Project Structure

```
src/
├── components/
│   ├── Header.jsx
│   ├── ProofOfThought.jsx
│   ├── CognitiveAptitude.jsx
│   ├── CurrentAssignment.jsx
│   └── ActionCards.jsx
├── pages/
│   └── Dashboard.jsx
├── services/
│   └── DatabaseService.js
├── App.jsx
├── main.jsx
└── index.css
```

## Technologies

- React 18+
- Tailwind CSS
- Recharts (for radar chart)
- React Router (for navigation)
- React Flow (ready for Logic Tree Canvas)
