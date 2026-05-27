import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import QuizGenerator from './pages/QuizGenerator'
import StudyPlanner from './pages/StudyPlanner'
import ResumeBuilder from './pages/ResumeBuilder'
import SkillGapAnalyzer from './pages/SkillGapAnalyzer'
import Recommendations from './pages/Recommendations'
import Analytics from './pages/Analytics'
import Settings from './pages/Settings'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/quiz" element={<QuizGenerator />} />
        <Route path="/study-planner" element={<StudyPlanner />} />
        <Route path="/resume" element={<ResumeBuilder />} />
        <Route path="/skill-gap" element={<SkillGapAnalyzer />} />
        <Route path="/recommendations" element={<Recommendations />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
