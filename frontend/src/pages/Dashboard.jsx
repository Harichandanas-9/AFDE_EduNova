import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Sparkles, BookOpenCheck, CalendarRange, FileText, Target, Flame, TrendingUp, Activity,
} from 'lucide-react'
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
} from 'recharts'
import GlassCard from '../components/GlassCard'
import PageHeader from '../components/PageHeader'
import { recentQuizResults, recentQuizzes, listStudyPlans } from '../utils/api'

const STATS = (q, p, avg, streak) => ([
  { label: 'Quizzes Taken',     value: q,     icon: BookOpenCheck, accent: 'from-mint-300 to-mint-500' },
  { label: 'Study Plans',       value: p,     icon: CalendarRange, accent: 'from-sea-300 to-sea-500' },
  { label: 'Avg Quiz Score',    value: `${avg}%`, icon: TrendingUp, accent: 'from-lavender-300 to-lavender-500' },
  { label: 'Current Streak',    value: `${streak}d`, icon: Flame,    accent: 'from-blush-300 to-blush-500' },
])

const radarData = [
  { skill: 'Programming', value: 78 },
  { skill: 'DSA',         value: 62 },
  { skill: 'System Design',value: 51 },
  { skill: 'Databases',   value: 70 },
  { skill: 'Communication',value: 82 },
  { skill: 'Career Prep', value: 60 },
]

export default function Dashboard() {
  const [quizCount, setQuizCount] = useState(0)
  const [planCount, setPlanCount] = useState(0)
  const [avgScore, setAvgScore]   = useState(0)
  const [history, setHistory]     = useState([])

  useEffect(() => {
    (async () => {
      try {
        const [results, quizzes, plans] = await Promise.all([
          recentQuizResults().catch(() => []),
          recentQuizzes().catch(() => []),
          listStudyPlans().catch(() => []),
        ])
        setQuizCount(quizzes.length)
        setPlanCount(plans.length)
        if (results.length) {
          const avg = results.reduce((s, r) => s + (r.score || 0), 0) / results.length
          setAvgScore(Math.round(avg))
          setHistory(
            results.slice(0, 10).reverse().map((r, i) => ({ name: `Q${i + 1}`, score: r.score })),
          )
        }
      } catch (_) { /* ignore */ }
    })()
  }, [])

  const stats = STATS(quizCount, planCount, avgScore, 7)

  return (
    <>
      <PageHeader
        title="Welcome to EduNova"
        subtitle="Your AI Career & Learning Copilot — let's grow today."
        icon={Sparkles}
      />

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s, i) => {
          const Icon = s.icon
          return (
            <GlassCard key={s.label} delay={i * 0.05}>
              <div className="flex items-start justify-between">
                <div>
                  <div className="text-slate-500 text-xs uppercase tracking-wider">{s.label}</div>
                  <div className="mt-2 text-2xl sm:text-3xl font-extrabold heading-gradient">{s.value}</div>
                </div>
                <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${s.accent} flex items-center justify-center text-white shadow-md`}>
                  <Icon className="w-5 h-5" />
                </div>
              </div>
            </GlassCard>
          )
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-4">
        <GlassCard className="lg:col-span-2">
          <div className="flex items-center justify-between mb-3">
            <div>
              <div className="font-display font-bold text-lg">Quiz Performance</div>
              <div className="text-slate-500 text-xs">Recent quiz scores</div>
            </div>
            <Activity className="w-5 h-5 text-lavender-500" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={history.length ? history : [{ name: 'Start', score: 0 }]}>
                <defs>
                  <linearGradient id="grad-score" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#7a5dff" stopOpacity={0.7}/>
                    <stop offset="100%" stopColor="#7a5dff" stopOpacity={0.05}/>
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} />
                <Tooltip />
                <Area type="monotone" dataKey="score" stroke="#5f43e3" strokeWidth={2.5} fill="url(#grad-score)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        <GlassCard>
          <div className="font-display font-bold text-lg">Skill Radar</div>
          <div className="text-slate-500 text-xs mb-2">Your current skill profile</div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="#e2e8f0" />
                <PolarAngleAxis dataKey="skill" tick={{ fontSize: 10 }} />
                <PolarRadiusAxis tick={{ fontSize: 9 }} angle={30} domain={[0, 100]} />
                <Radar name="You" dataKey="value" stroke="#1976bf" fill="#1976bf" fillOpacity={0.35} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
        {[
          { title: 'Generate a Quiz',    desc: 'Test your knowledge', to: '/quiz',          icon: BookOpenCheck, accent: 'bg-gradient-mint' },
          { title: 'Build a Study Plan', desc: '8-week roadmap',      to: '/study-planner', icon: CalendarRange, accent: 'bg-gradient-soft' },
          { title: 'Polish your Resume', desc: 'ATS-ready',           to: '/resume',        icon: FileText,      accent: 'bg-gradient-edu' },
          { title: 'Find skill gaps',    desc: 'Plan ahead',          to: '/skill-gap',     icon: Target,        accent: 'bg-gradient-mint' },
        ].map((card, i) => {
          const Icon = card.icon
          return (
            <Link key={card.title} to={card.to}>
              <GlassCard delay={i * 0.05}>
                <div className={`w-10 h-10 rounded-xl ${card.accent} flex items-center justify-center mb-3`}>
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <div className="font-bold">{card.title}</div>
                <div className="text-xs text-slate-500">{card.desc}</div>
              </GlassCard>
            </Link>
          )
        })}
      </div>
    </>
  )
}
