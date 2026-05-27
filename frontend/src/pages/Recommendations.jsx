import { useState } from 'react'
import { Sparkles, ExternalLink } from 'lucide-react'
import PageHeader from '../components/PageHeader'
import GlassCard from '../components/GlassCard'
import LoadingSkeleton from '../components/LoadingSkeleton'
import { useToast } from '../hooks/useToast'
import { getRecommendations } from '../utils/api'

const TYPE_COLORS = {
  course:        'bg-sea-100 text-sea-700 border-sea-200',
  youtube:       'bg-blush-100 text-blush-700 border-blush-200',
  doc:           'bg-lavender-100 text-lavender-700 border-lavender-200',
  certification: 'bg-mint-100 text-mint-700 border-mint-200',
  practice:      'bg-slate-100 text-slate-700 border-slate-200',
}

export default function Recommendations() {
  const toast = useToast()
  const [role, setRole]       = useState('Backend Engineer')
  const [interests, setI]     = useState('Python, Databases, System design')
  const [weak, setWeak]       = useState('System design, SQL')
  const [style, setStyle]     = useState('video')
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(false)

  const onFetch = async () => {
    setLoading(true)
    try {
      const res = await getRecommendations({
        target_role: role,
        interests: interests.split(',').map((s) => s.trim()).filter(Boolean),
        weak_skills: weak.split(',').map((s) => s.trim()).filter(Boolean),
        learning_style: style,
      })
      setData(res); toast.success('Recommendations ready!')
    } catch { toast.error('Could not fetch recommendations.') }
    finally { setLoading(false) }
  }

  return (
    <>
      <PageHeader title="Recommendations" subtitle="Hand-picked courses, videos, docs, and practice" icon={Sparkles} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <GlassCard>
          <div className="space-y-3">
            <div><label className="label-text">Target role</label>
              <input className="input-field" value={role} onChange={(e) => setRole(e.target.value)} /></div>
            <div><label className="label-text">Interests</label>
              <input className="input-field" value={interests} onChange={(e) => setI(e.target.value)} /></div>
            <div><label className="label-text">Weak skills</label>
              <input className="input-field" value={weak} onChange={(e) => setWeak(e.target.value)} /></div>
            <div><label className="label-text">Learning style</label>
              <select className="input-field" value={style} onChange={(e) => setStyle(e.target.value)}>
                <option value="video">Video</option><option value="reading">Reading</option><option value="hands-on">Hands-on</option>
              </select></div>
            <button onClick={onFetch} disabled={loading} className="btn-primary w-full">
              {loading ? 'Curating…' : 'Get recommendations'}
            </button>
          </div>
        </GlassCard>

        <div className="lg:col-span-2 space-y-3">
          {loading && <GlassCard><LoadingSkeleton rows={6} /></GlassCard>}
          {data && (
            <>
              {data.notes && <GlassCard><div className="text-sm text-slate-600">{data.notes}</div></GlassCard>}
              {data.items.map((it, i) => (
                <GlassCard key={i} delay={i * 0.04}>
                  <div className="flex flex-col sm:flex-row sm:items-start gap-3 sm:justify-between">
                    <div>
                      <div className="flex flex-wrap items-center gap-2 mb-1">
                        <div className="font-bold">{it.title}</div>
                        <span className={`chip ${TYPE_COLORS[it.type] || ''}`}>{it.type}</span>
                        {it.level && <span className="chip">{it.level}</span>}
                        {it.duration && <span className="chip">{it.duration}</span>}
                      </div>
                      <div className="text-xs text-slate-500">{it.provider}</div>
                      <div className="text-sm mt-1 text-slate-700">{it.reason}</div>
                    </div>
                    {it.url && (
                      <a href={it.url} target="_blank" rel="noreferrer" className="btn-secondary !py-2 shrink-0">
                        <ExternalLink className="w-4 h-4" /> Open
                      </a>
                    )}
                  </div>
                </GlassCard>
              ))}
            </>
          )}
        </div>
      </div>
    </>
  )
}
