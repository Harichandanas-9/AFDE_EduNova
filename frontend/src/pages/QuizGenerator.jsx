import { useState } from 'react'
import { BookOpenCheck, Play, RotateCcw, Trophy } from 'lucide-react'
import { motion } from 'framer-motion'
import PageHeader from '../components/PageHeader'
import GlassCard from '../components/GlassCard'
import LoadingSkeleton from '../components/LoadingSkeleton'
import { useToast } from '../hooks/useToast'
import { generateQuiz, submitQuiz } from '../utils/api'

const DIFFICULTIES = ['easy', 'medium', 'hard']
const TYPES = ['mcq', 'true_false', 'short', 'coding', 'mixed']

export default function QuizGenerator() {
  const toast = useToast()
  const [topic, setTopic] = useState('Python basics')
  const [difficulty, setDifficulty] = useState('medium')
  const [count, setCount] = useState(5)
  const [type, setType] = useState('mcq')
  const [quiz, setQuiz] = useState(null)
  const [answers, setAnswers] = useState({})
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [startTime, setStartTime] = useState(null)

  const onGenerate = async () => {
    setLoading(true); setResult(null); setAnswers({}); setQuiz(null)
    try {
      const data = await generateQuiz({ topic, difficulty, question_count: count, question_type: type })
      setQuiz(data); setStartTime(Date.now()); toast.success('Quiz generated!')
    } catch { toast.error('Could not generate quiz.') }
    finally { setLoading(false) }
  }

  const onSubmit = async () => {
    if (!quiz) return
    setSubmitting(true)
    try {
      const duration = Math.round((Date.now() - (startTime || Date.now())) / 1000)
      const payload = {
        quiz_id: quiz.quiz_id,
        duration_seconds: duration,
        answers: quiz.questions.map((q) => ({ question_id: q.id, answer: answers[q.id] || '' })),
      }
      const data = await submitQuiz(payload)
      setResult(data)
      toast.success(`You scored ${data.score}%`)
    } catch { toast.error('Submission failed.') }
    finally { setSubmitting(false) }
  }

  const reset = () => { setQuiz(null); setResult(null); setAnswers({}) }

  return (
    <>
      <PageHeader
        title="Smart Quiz Generator"
        subtitle="Adaptive AI-generated quizzes for any topic"
        icon={BookOpenCheck}
        actions={quiz && (
          <button onClick={reset} className="btn-secondary"><RotateCcw className="w-4 h-4" /> Reset</button>
        )}
      />

      {/* Generator form */}
      {!quiz && (
        <GlassCard>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="sm:col-span-2">
              <label className="label-text">Topic</label>
              <input className="input-field" value={topic} onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g. JavaScript closures, Linear algebra, REST APIs" />
            </div>
            <div>
              <label className="label-text">Difficulty</label>
              <select className="input-field" value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
                {DIFFICULTIES.map((d) => <option key={d}>{d}</option>)}
              </select>
            </div>
            <div>
              <label className="label-text">Question Type</label>
              <select className="input-field" value={type} onChange={(e) => setType(e.target.value)}>
                {TYPES.map((t) => <option key={t} value={t}>{t.toUpperCase()}</option>)}
              </select>
            </div>
            <div>
              <label className="label-text">Number of Questions</label>
              <input type="number" min={1} max={20} className="input-field"
                value={count} onChange={(e) => setCount(Number(e.target.value))} />
            </div>
            <div className="sm:col-span-2 flex justify-end">
              <button onClick={onGenerate} disabled={loading} className="btn-primary">
                <Play className="w-4 h-4" /> {loading ? 'Generating…' : 'Generate Quiz'}
              </button>
            </div>
          </div>
          {loading && <div className="mt-5"><LoadingSkeleton rows={5} /></div>}
        </GlassCard>
      )}

      {/* Quiz */}
      {quiz && !result && (
        <div className="space-y-4">
          {quiz.questions.map((q, idx) => (
            <GlassCard key={q.id} delay={idx * 0.04}>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-gradient-edu text-white flex items-center justify-center font-bold text-sm shrink-0">
                  {idx + 1}
                </div>
                <div className="flex-1">
                  <div className="font-semibold mb-3">{q.question}</div>
                  {q.options ? (
                    <div className="grid sm:grid-cols-2 gap-2">
                      {q.options.map((opt) => (
                        <label key={opt} className={`cursor-pointer rounded-xl border px-3 py-2.5 text-sm flex items-center gap-2 transition
                          ${answers[q.id] === opt ? 'border-lavender-400 bg-lavender-50 shadow-glow' : 'border-lavender-200 hover:bg-white'}`}>
                          <input type="radio" name={`q-${q.id}`} className="accent-lavender-500"
                            checked={answers[q.id] === opt}
                            onChange={() => setAnswers((a) => ({ ...a, [q.id]: opt }))} />
                          <span>{opt}</span>
                        </label>
                      ))}
                    </div>
                  ) : (
                    <input className="input-field" placeholder="Your answer"
                      value={answers[q.id] || ''} onChange={(e) => setAnswers((a) => ({ ...a, [q.id]: e.target.value }))} />
                  )}
                </div>
              </div>
            </GlassCard>
          ))}
          <div className="flex justify-end">
            <button onClick={onSubmit} disabled={submitting} className="btn-primary">
              <Trophy className="w-4 h-4" /> {submitting ? 'Scoring…' : 'Submit Quiz'}
            </button>
          </div>
        </div>
      )}

      {/* Result */}
      {result && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          <GlassCard>
            <div className="flex flex-col sm:flex-row items-center sm:justify-between gap-4">
              <div>
                <div className="font-display font-bold text-xl">Your Result</div>
                <div className="text-slate-500 text-sm">{result.feedback}</div>
              </div>
              <div className="text-center">
                <div className="text-5xl font-extrabold heading-gradient">{result.score}%</div>
                <div className="text-xs uppercase tracking-wider text-slate-500">
                  {result.correct} / {result.total} correct
                </div>
                <div className="chip mt-2 !bg-mint-100 !text-mint-700 !border-mint-200">
                  Next difficulty: {result.suggested_difficulty}
                </div>
              </div>
            </div>
          </GlassCard>

          <div className="space-y-3">
            {result.per_question.map((q, i) => (
              <GlassCard key={q.id} delay={i * 0.03}>
                <div className="text-sm font-semibold">{i + 1}. {q.question}</div>
                <div className="mt-2 grid sm:grid-cols-2 gap-2 text-sm">
                  <div className={`rounded-lg px-3 py-2 ${q.is_correct ? 'bg-mint-50 text-mint-700' : 'bg-blush-50 text-blush-700'}`}>
                    Your answer: <strong>{q.user_answer || '—'}</strong>
                  </div>
                  <div className="rounded-lg px-3 py-2 bg-sea-50 text-sea-700">
                    Correct: <strong>{q.correct_answer}</strong>
                  </div>
                </div>
                {q.explanation && <div className="text-xs text-slate-500 mt-2">💡 {q.explanation}</div>}
              </GlassCard>
            ))}
          </div>

          <div className="flex justify-end">
            <button onClick={reset} className="btn-primary"><RotateCcw className="w-4 h-4" /> Take Another</button>
          </div>
        </motion.div>
      )}
    </>
  )
}
