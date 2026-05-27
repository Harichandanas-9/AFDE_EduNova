import { useState } from 'react'
import { Target } from 'lucide-react'
import {
  ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
} from 'recharts'
import PageHeader from '../components/PageHeader'
import GlassCard from '../components/GlassCard'
import LoadingSkeleton from '../components/LoadingSkeleton'
import { useToast } from '../hooks/useToast'
import { analyzeSkillGap } from '../utils/api'

export default function SkillGapAnalyzer() {
  const toast = useToast()
  const [skills, setSkills] = useState('Python, SQL, Git, REST API')
  const [role, setRole] = useState('Data Scientist')
  const [years, setYears] = useState(1)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const onAnalyze = async () => {
    setLoading(true)
    try {
      const data = await analyzeSkillGap({
        current_skills: skills.split(',').map((s) => s.trim()).filter(Boolean),
        target_role: role,
        years_experience: years,
      })
      setResult(data); toast.success('Analysis complete.')
    } catch { toast.error('Could not analyze.') }
    finally { setLoading(false) }
  }

  const radarData = (result?.skill_breakdown || []).map((s) => ({ skill: s.skill, value: s.has ? 100 : 30, importance: s.importance * 100 }))
  const barData = (result?.skill_breakdown || []).map((s) => ({ skill: s.skill, importance: Math.round(s.importance * 100), has: s.has ? 100 : 0 }))

  return (
    <>
      <PageHeader title="Skill Gap Analyzer" subtitle="Compare your skills against the target role" icon={Target} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <GlassCard>
          <div className="space-y-3">
            <div>
              <label className="label-text">Target role</label>
              <input className="input-field" value={role} onChange={(e) => setRole(e.target.value)} />
            </div>
            <div>
              <label className="label-text">Years experience</label>
              <input type="number" min={0} max={50} className="input-field" value={years} onChange={(e) => setYears(Number(e.target.value))} />
            </div>
            <div>
              <label className="label-text">Your current skills (comma separated)</label>
              <textarea rows={4} className="input-field" value={skills} onChange={(e) => setSkills(e.target.value)} />
            </div>
            <button onClick={onAnalyze} disabled={loading} className="btn-primary w-full">
              {loading ? 'Analyzing…' : 'Analyze'}
            </button>
          </div>
        </GlassCard>

        <div className="lg:col-span-2 space-y-4">
          {loading && <GlassCard><LoadingSkeleton rows={6} /></GlassCard>}
          {result && (
            <>
              <GlassCard>
                <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
                  <div>
                    <div className="font-display font-bold text-xl">{result.target_role}</div>
                    <div className="text-slate-500 text-sm">Estimated weeks to ready: {result.estimated_weeks_to_ready}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-5xl font-extrabold heading-gradient">{result.readiness_percent}%</div>
                    <div className="text-xs uppercase tracking-wider text-slate-500">readiness</div>
                  </div>
                </div>
                <div className="mt-3 h-2 rounded-full bg-lavender-100 overflow-hidden">
                  <div className="h-full bg-gradient-edu transition-all" style={{ width: `${result.readiness_percent}%` }} />
                </div>
              </GlassCard>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <GlassCard>
                  <div className="font-display font-bold mb-2">Skill radar</div>
                  <div className="h-64">
                    <ResponsiveContainer>
                      <RadarChart data={radarData}>
                        <PolarGrid stroke="#e2e8f0" />
                        <PolarAngleAxis dataKey="skill" tick={{ fontSize: 10 }} />
                        <PolarRadiusAxis tick={{ fontSize: 9 }} domain={[0, 100]} />
                        <Radar name="You" dataKey="value" stroke="#7a5dff" fill="#7a5dff" fillOpacity={0.35} />
                        <Radar name="Role importance" dataKey="importance" stroke="#1976bf" fill="#1976bf" fillOpacity={0.15} />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </GlassCard>
                <GlassCard>
                  <div className="font-display font-bold mb-2">Skill importance</div>
                  <div className="h-64">
                    <ResponsiveContainer>
                      <BarChart data={barData}>
                        <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" />
                        <XAxis dataKey="skill" tick={{ fontSize: 10 }} interval={0} angle={-25} textAnchor="end" height={50} />
                        <YAxis tick={{ fontSize: 10 }} />
                        <Tooltip />
                        <Bar dataKey="importance" radius={[6,6,0,0]} fill="#5f43e3" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </GlassCard>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <GlassCard>
                  <div className="font-display font-bold mb-2">Matched skills</div>
                  <div className="flex flex-wrap gap-2">
                    {result.matched_skills.map((s) => (
                      <span key={s} className="chip !bg-mint-100 !text-mint-700 !border-mint-200">{s}</span>
                    ))}
                    {result.matched_skills.length === 0 && <div className="text-sm text-slate-500">No matches yet — start with the missing list.</div>}
                  </div>
                </GlassCard>
                <GlassCard>
                  <div className="font-display font-bold mb-2">Missing skills</div>
                  <div className="flex flex-wrap gap-2">
                    {result.missing_skills.map((s) => (
                      <span key={s} className="chip !bg-blush-100 !text-blush-700 !border-blush-200">{s}</span>
                    ))}
                    {result.missing_skills.length === 0 && <div className="text-sm text-mint-700">You're well-aligned! 🎉</div>}
                  </div>
                </GlassCard>
              </div>

              <GlassCard>
                <div className="font-display font-bold mb-2">Learning roadmap</div>
                <ul className="list-disc pl-5 text-sm text-slate-700 space-y-1">
                  {result.learning_roadmap.map((r, i) => <li key={i}>{r}</li>)}
                </ul>
              </GlassCard>
              <GlassCard>
                <div className="font-display font-bold mb-2">Project ideas</div>
                <ul className="list-disc pl-5 text-sm text-slate-700 space-y-1">
                  {result.project_ideas.map((p, i) => <li key={i}>{p}</li>)}
                </ul>
              </GlassCard>
            </>
          )}
        </div>
      </div>
    </>
  )
}
