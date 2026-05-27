import { useState } from 'react'
import { FileText, Plus, Trash2, Download } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import PageHeader from '../components/PageHeader'
import GlassCard from '../components/GlassCard'
import LoadingSkeleton from '../components/LoadingSkeleton'
import { useToast } from '../hooks/useToast'
import { buildResume } from '../utils/api'

const empty = {
  full_name: 'Hari Chandana',
  email: 'me@example.com',
  phone: '',
  target_role: 'Backend Engineer',
  template: 'modern',
  skills: ['Python', 'FastAPI', 'SQL', 'Docker'],
  experience: [{ company: 'Acme Corp', role: 'SDE', duration: '2023 — Present', description: '', achievements: ['Shipped a critical service'] }],
  education: [{ institution: 'XYZ University', degree: 'B.Tech, CS', duration: '2018 — 2022' }],
  projects: [{ name: 'EduNova AI', description: 'AI learning copilot', tech_stack: ['React', 'FastAPI', 'LangGraph'] }],
  achievements: ['Top 5% in coding contest 2023'],
}

export default function ResumeBuilder() {
  const toast = useToast()
  const [form, setForm] = useState(empty)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  const updateExp = (i, k, v) => setForm((f) => ({ ...f, experience: f.experience.map((e, ix) => ix === i ? { ...e, [k]: v } : e) }))
  const updateEdu = (i, k, v) => setForm((f) => ({ ...f, education:  f.education.map((e, ix) => ix === i ? { ...e, [k]: v } : e) }))
  const updatePrj = (i, k, v) => setForm((f) => ({ ...f, projects:   f.projects.map((p, ix) => ix === i ? { ...p, [k]: v } : p) }))

  const addExp = () => set('experience', [...form.experience, { company: '', role: '', duration: '', description: '', achievements: [] }])
  const delExp = (i) => set('experience', form.experience.filter((_, ix) => ix !== i))
  const addEdu = () => set('education', [...form.education, { institution: '', degree: '', duration: '' }])
  const delEdu = (i) => set('education', form.education.filter((_, ix) => ix !== i))
  const addPrj = () => set('projects', [...form.projects, { name: '', description: '', tech_stack: [] }])
  const delPrj = (i) => set('projects', form.projects.filter((_, ix) => ix !== i))

  const onBuild = async () => {
    setLoading(true)
    try {
      const data = await buildResume({
        ...form,
        skills: typeof form.skills === 'string' ? form.skills.split(',').map((s) => s.trim()).filter(Boolean) : form.skills,
        projects: form.projects.map((p) => ({ ...p, tech_stack: typeof p.tech_stack === 'string' ? p.tech_stack.split(',').map((s) => s.trim()) : p.tech_stack })),
      })
      setResult(data); toast.success('Resume generated.')
    } catch { toast.error('Could not build resume.') }
    finally { setLoading(false) }
  }

  const downloadMd = () => {
    if (!result?.markdown) return
    const blob = new Blob([result.markdown], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `${form.full_name.replace(/\s+/g, '_')}_resume.md`
    a.click(); URL.revokeObjectURL(url)
  }

  return (
    <>
      <PageHeader title="AI Resume Builder" subtitle="ATS-friendly, AI-optimized" icon={FileText}
        actions={result && (
          <button onClick={downloadMd} className="btn-secondary"><Download className="w-4 h-4" /> Download .md</button>
        )} />

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        {/* Form */}
        <GlassCard className="lg:col-span-3 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div><label className="label-text">Full name</label><input className="input-field" value={form.full_name} onChange={(e) => set('full_name', e.target.value)} /></div>
            <div><label className="label-text">Target role</label><input className="input-field" value={form.target_role} onChange={(e) => set('target_role', e.target.value)} /></div>
            <div><label className="label-text">Email</label><input className="input-field" value={form.email} onChange={(e) => set('email', e.target.value)} /></div>
            <div><label className="label-text">Phone</label><input className="input-field" value={form.phone} onChange={(e) => set('phone', e.target.value)} /></div>
            <div className="sm:col-span-2">
              <label className="label-text">Template</label>
              <div className="flex gap-2 flex-wrap">
                {['modern', 'classic', 'minimal', 'creative'].map((t) => (
                  <button key={t} onClick={() => set('template', t)}
                    className={`chip ${form.template === t ? '!bg-gradient-edu !text-white !border-transparent' : ''}`}>
                    {t}
                  </button>
                ))}
              </div>
            </div>
            <div className="sm:col-span-2">
              <label className="label-text">Skills (comma separated)</label>
              <input className="input-field"
                value={Array.isArray(form.skills) ? form.skills.join(', ') : form.skills}
                onChange={(e) => set('skills', e.target.value.split(',').map((s) => s.trim()))} />
            </div>
          </div>

          {/* Experience */}
          <Section title="Experience" onAdd={addExp}>
            {form.experience.map((e, i) => (
              <GlassCard key={i} hover={false} className="!p-4">
                <div className="flex justify-between items-center mb-2">
                  <div className="font-semibold text-sm">Role #{i + 1}</div>
                  <button onClick={() => delExp(i)} className="text-blush-600"><Trash2 className="w-4 h-4" /></button>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <input className="input-field" placeholder="Role" value={e.role} onChange={(ev) => updateExp(i, 'role', ev.target.value)} />
                  <input className="input-field" placeholder="Company" value={e.company} onChange={(ev) => updateExp(i, 'company', ev.target.value)} />
                  <input className="input-field col-span-2" placeholder="Duration" value={e.duration} onChange={(ev) => updateExp(i, 'duration', ev.target.value)} />
                  <textarea rows={2} className="input-field col-span-2" placeholder="Description"
                    value={e.description} onChange={(ev) => updateExp(i, 'description', ev.target.value)} />
                </div>
              </GlassCard>
            ))}
          </Section>

          {/* Projects */}
          <Section title="Projects" onAdd={addPrj}>
            {form.projects.map((p, i) => (
              <GlassCard key={i} hover={false} className="!p-4">
                <div className="flex justify-between items-center mb-2">
                  <div className="font-semibold text-sm">Project #{i + 1}</div>
                  <button onClick={() => delPrj(i)} className="text-blush-600"><Trash2 className="w-4 h-4" /></button>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <input className="input-field col-span-2" placeholder="Name" value={p.name} onChange={(e) => updatePrj(i, 'name', e.target.value)} />
                  <textarea rows={2} className="input-field col-span-2" placeholder="Description"
                    value={p.description} onChange={(e) => updatePrj(i, 'description', e.target.value)} />
                  <input className="input-field col-span-2" placeholder="Tech stack (comma separated)"
                    value={Array.isArray(p.tech_stack) ? p.tech_stack.join(', ') : p.tech_stack}
                    onChange={(e) => updatePrj(i, 'tech_stack', e.target.value.split(',').map((s) => s.trim()))} />
                </div>
              </GlassCard>
            ))}
          </Section>

          {/* Education */}
          <Section title="Education" onAdd={addEdu}>
            {form.education.map((e, i) => (
              <GlassCard key={i} hover={false} className="!p-4">
                <div className="flex justify-between items-center mb-2">
                  <div className="font-semibold text-sm">Education #{i + 1}</div>
                  <button onClick={() => delEdu(i)} className="text-blush-600"><Trash2 className="w-4 h-4" /></button>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <input className="input-field col-span-2" placeholder="Institution" value={e.institution} onChange={(ev) => updateEdu(i, 'institution', ev.target.value)} />
                  <input className="input-field" placeholder="Degree" value={e.degree} onChange={(ev) => updateEdu(i, 'degree', ev.target.value)} />
                  <input className="input-field" placeholder="Duration" value={e.duration} onChange={(ev) => updateEdu(i, 'duration', ev.target.value)} />
                </div>
              </GlassCard>
            ))}
          </Section>

          <div className="flex justify-end">
            <button className="btn-primary" disabled={loading} onClick={onBuild}>
              {loading ? 'Generating…' : 'Generate resume'}
            </button>
          </div>
        </GlassCard>

        {/* Preview */}
        <GlassCard className="lg:col-span-2 self-start">
          <div className="font-display font-bold text-lg mb-2">Live preview</div>
          {loading && <LoadingSkeleton rows={8} />}
          {!loading && !result && (
            <div className="text-sm text-slate-500">Generate to see your AI-polished resume here.</div>
          )}
          {result && (
            <>
              <div className="flex items-center justify-between mb-3">
                <div className="chip !bg-mint-100 !text-mint-700 !border-mint-200">ATS score: {result.ats_score}%</div>
                <div className="text-xs text-slate-400">Template: {result.template}</div>
              </div>
              <div className="prose-chat text-sm bg-white/70 rounded-xl p-4 max-h-[60vh] overflow-y-auto">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{result.markdown}</ReactMarkdown>
              </div>
              {result.suggestions?.length > 0 && (
                <div className="mt-3">
                  <div className="text-xs font-semibold uppercase text-slate-500 mb-1">Suggestions</div>
                  <ul className="list-disc pl-5 text-xs text-slate-600 space-y-0.5">
                    {result.suggestions.map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
              )}
            </>
          )}
        </GlassCard>
      </div>
    </>
  )
}

function Section({ title, onAdd, children }) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="font-display font-bold">{title}</div>
        <button onClick={onAdd} className="chip"><Plus className="w-3.5 h-3.5" /> Add</button>
      </div>
      {children}
    </div>
  )
}
