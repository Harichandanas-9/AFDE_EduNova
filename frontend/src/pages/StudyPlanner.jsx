import { useState } from 'react'
import { CalendarRange, CheckCircle2 } from 'lucide-react'
import PageHeader from '../components/PageHeader'
import GlassCard from '../components/GlassCard'
import LoadingSkeleton from '../components/LoadingSkeleton'
import { useToast } from '../hooks/useToast'
import { createStudyPlan } from '../utils/api'

export default function StudyPlanner() {
  const toast = useToast()
  const [form, setForm] = useState({
    goal: 'Become a Full-stack Developer',
    current_level: 'beginner',
    target_role: 'Full-stack Developer',
    available_hours_per_week: 12,
    duration_weeks: 8,
  })
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState({})

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  const onCreate = async () => {
    setLoading(true); setPlan(null); setDone({})
    try {
      const data = await createStudyPlan(form)
      setPlan(data); toast.success('Plan ready!')
    } catch { toast.error('Could not create plan.') }
    finally { setLoading(false) }
  }

  const toggleDone = (w) => setDone((d) => ({ ...d, [w]: !d[w] }))
  const completion = plan ? Math.round(100 * Object.values(done).filter(Boolean).length / Math.max(1, plan.schedule.length)) : 0

  return (
    <>
      <PageHeader
        title="Adaptive Study Planner"
        subtitle="A personalized week-by-week roadmap for your goal"
        icon={CalendarRange}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <GlassCard className="lg:col-span-1">
          <div className="space-y-3">
            <div>
              <label className="label-text">Goal</label>
              <textarea rows={2} className="input-field" value={form.goal} onChange={(e) => set('goal', e.target.value)} />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="label-text">Level</label>
                <select className="input-field" value={form.current_level} onChange={(e) => set('current_level', e.target.value)}>
                  <option>beginner</option><option>intermediate</option><option>advanced</option>
                </select>
              </div>
              <div>
                <label className="label-text">Target role</label>
                <input className="input-field" value={form.target_role} onChange={(e) => set('target_role', e.target.value)} />
              </div>
              <div>
                <label className="label-text">Hours/week</label>
                <input type="number" min={1} max={80} className="input-field"
                  value={form.available_hours_per_week} onChange={(e) => set('available_hours_per_week', Number(e.target.value))} />
              </div>
              <div>
                <label className="label-text">Weeks</label>
                <input type="number" min={1} max={52} className="input-field"
                  value={form.duration_weeks} onChange={(e) => set('duration_weeks', Number(e.target.value))} />
              </div>
            </div>
            <button onClick={onCreate} disabled={loading} className="btn-primary w-full">
              {loading ? 'Building…' : 'Create plan'}
            </button>
          </div>
        </GlassCard>

        <div className="lg:col-span-2 space-y-4">
          {loading && <GlassCard><LoadingSkeleton rows={6} /></GlassCard>}
          {plan && (
            <>
              <GlassCard>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-display font-bold text-lg">{plan.goal}</div>
                    <div className="text-slate-500 text-sm">{plan.overview}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-3xl font-extrabold heading-gradient">{completion}%</div>
                    <div className="text-xs uppercase tracking-wider text-slate-500">complete</div>
                  </div>
                </div>
                <div className="mt-3 h-2 rounded-full bg-lavender-100 overflow-hidden">
                  <div className="h-full bg-gradient-edu transition-all" style={{ width: `${completion}%` }} />
                </div>
              </GlassCard>

              <div className="relative pl-5">
                <div className="absolute left-1.5 top-0 bottom-0 w-0.5 bg-lavender-200" />
                {plan.schedule.map((w, i) => (
                  <GlassCard key={w.week} delay={i * 0.03} className="mb-3 relative">
                    <div className={`absolute -left-[26px] top-6 w-3 h-3 rounded-full ring-2 ring-white ${done[w.week] ? 'bg-mint-500' : 'bg-lavender-400'}`} />
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="font-bold">{w.title}</div>
                        <div className="text-xs text-slate-500">
                          Focus: {w.focus_areas?.join(', ')}
                        </div>
                      </div>
                      <button onClick={() => toggleDone(w.week)}
                        className={`shrink-0 chip ${done[w.week] ? '!bg-mint-100 !text-mint-700 !border-mint-200' : ''}`}>
                        <CheckCircle2 className="w-3.5 h-3.5" /> {done[w.week] ? 'Done' : 'Mark done'}
                      </button>
                    </div>
                    <div className="mt-2 grid sm:grid-cols-3 gap-2 text-xs">
                      <div className="rounded-lg bg-sea-50 text-sea-700 px-3 py-2">
                        <div className="uppercase tracking-wider text-[10px]">Topics</div>
                        {(w.topics || []).join(' · ')}
                      </div>
                      <div className="rounded-lg bg-lavender-50 text-lavender-700 px-3 py-2">
                        <div className="uppercase tracking-wider text-[10px]">Resources</div>
                        {(w.resources || []).join(' · ')}
                      </div>
                      <div className="rounded-lg bg-mint-50 text-mint-700 px-3 py-2">
                        <div className="uppercase tracking-wider text-[10px]">Practice</div>
                        {(w.practice || []).join(' · ')}
                      </div>
                    </div>
                    {w.milestone && (
                      <div className="mt-2 text-xs text-blush-700 bg-blush-50 rounded-lg px-3 py-2">
                        🏁 {w.milestone}
                      </div>
                    )}
                  </GlassCard>
                ))}
              </div>
            </>
          )}
          {!plan && !loading && (
            <GlassCard>
              <div className="text-slate-500 text-sm">
                Fill in your goal and target role on the left, then hit <em>Create plan</em>. Your AI will produce a week-by-week roadmap with topics, resources, and milestones.
              </div>
            </GlassCard>
          )}
        </div>
      </div>
    </>
  )
}
