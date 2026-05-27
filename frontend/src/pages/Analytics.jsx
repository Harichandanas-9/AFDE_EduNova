import { useEffect, useState } from 'react'
import { BarChart3 } from 'lucide-react'
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import PageHeader from '../components/PageHeader'
import GlassCard from '../components/GlassCard'
import { recentQuizResults, recentQuizzes } from '../utils/api'

const COLORS = ['#1976bf', '#7a5dff', '#1fbf89', '#ff85a8', '#46d2a4']

export default function Analytics() {
  const [results, setResults] = useState([])
  const [quizzes, setQuizzes] = useState([])

  useEffect(() => {
    Promise.all([recentQuizResults().catch(() => []), recentQuizzes().catch(() => [])])
      .then(([r, q]) => { setResults(r); setQuizzes(q) })
  }, [])

  const byTopic = quizzes.reduce((acc, q) => { acc[q.topic] = (acc[q.topic] || 0) + 1; return acc }, {})
  const topicData = Object.entries(byTopic).map(([name, value]) => ({ name, value }))
  const scoreData = results.slice(0, 10).reverse().map((r, i) => ({ name: `Q${i + 1}`, score: r.score }))

  return (
    <>
      <PageHeader title="Analytics" subtitle="Your learning data at a glance" icon={BarChart3} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <GlassCard>
          <div className="font-display font-bold mb-2">Recent quiz scores</div>
          <div className="h-72">
            <ResponsiveContainer>
              <BarChart data={scoreData.length ? scoreData : [{ name: 'Start', score: 0 }]}>
                <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="score" radius={[8,8,0,0]} fill="#7a5dff" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        <GlassCard>
          <div className="font-display font-bold mb-2">Topic distribution</div>
          <div className="h-72">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={topicData.length ? topicData : [{ name: 'No data', value: 1 }]}
                  dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} innerRadius={45} paddingAngle={4}>
                  {(topicData.length ? topicData : [{}]).map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Legend verticalAlign="bottom" iconType="circle" />
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>
      </div>

      <GlassCard className="mt-4">
        <div className="font-display font-bold mb-3">Recent activity</div>
        <div className="divide-y divide-white/40">
          {results.length === 0 && <div className="text-sm text-slate-500 py-2">No activity yet. Take a quiz to get started!</div>}
          {results.slice(0, 8).map((r) => (
            <div key={r.id} className="flex items-center justify-between py-2 text-sm">
              <div>Quiz #{r.quiz_id} — {r.correct}/{r.total} correct</div>
              <div className="font-semibold">{r.score}%</div>
            </div>
          ))}
        </div>
      </GlassCard>
    </>
  )
}
