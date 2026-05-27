import { useEffect, useState } from 'react'
import { Settings as Cog, Server, ShieldCheck, Sparkles } from 'lucide-react'
import PageHeader from '../components/PageHeader'
import GlassCard from '../components/GlassCard'
import { health } from '../utils/api'
import { useStore } from '../store/useStore'

export default function Settings() {
  const sessionId = useStore((s) => s.sessionId)
  const [status, setStatus] = useState(null)

  useEffect(() => { health().then(setStatus).catch(() => setStatus({ status: 'down' })) }, [])

  return (
    <>
      <PageHeader title="Settings" subtitle="Configuration & system info" icon={Cog} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <GlassCard>
          <div className="flex items-center gap-2 mb-2 font-display font-bold"><Server className="w-4 h-4" /> Backend health</div>
          {!status && <div className="text-sm text-slate-500">Checking…</div>}
          {status && (
            <ul className="text-sm space-y-1">
              <li>Status: <span className={status.status === 'ok' ? 'text-mint-700' : 'text-blush-700'}>{status.status}</span></li>
              {status.app && <li>App: {status.app} v{status.version}</li>}
              {status.llm_provider && <li>LLM provider: <span className="chip">{status.llm_provider}</span></li>}
              {status.environment && <li>Environment: {status.environment}</li>}
            </ul>
          )}
        </GlassCard>

        <GlassCard>
          <div className="flex items-center gap-2 mb-2 font-display font-bold"><ShieldCheck className="w-4 h-4" /> Guardrails</div>
          <p className="text-sm text-slate-600">
            EduNova is restricted to education, learning, quizzes, study planning, resumes,
            interview prep, skill analysis, and career growth. Off-topic and unsafe content
            is blocked at the agent layer.
          </p>
        </GlassCard>

        <GlassCard>
          <div className="flex items-center gap-2 mb-2 font-display font-bold"><Sparkles className="w-4 h-4" /> Session</div>
          <p className="text-sm text-slate-600">Session ID</p>
          <code className="block mt-1 text-xs bg-slate-100 rounded p-2 break-all">{sessionId}</code>
        </GlassCard>

        <GlassCard>
          <div className="font-display font-bold mb-2">Theme</div>
          <p className="text-sm text-slate-600">
            Sea Blue · Lavender · White · Light Bluish Green · Light Pink — a glassmorphism palette
            designed for clarity and warmth.
          </p>
          <div className="mt-3 flex gap-2">
            {['#1976bf', '#7a5dff', '#ffffff', '#46d2a4', '#ff85a8'].map((c) => (
              <span key={c} className="w-8 h-8 rounded-lg border border-white/60 shadow-glass" style={{ background: c }} />
            ))}
          </div>
        </GlassCard>
      </div>
    </>
  )
}
