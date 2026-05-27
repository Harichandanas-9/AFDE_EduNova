import { useEffect, useRef, useState } from 'react'
import { Send, MessageSquare, Sparkles, RotateCcw } from 'lucide-react'
import PageHeader from '../components/PageHeader'
import GlassCard from '../components/GlassCard'
import ChatMessage, { TypingBubble } from '../components/ChatMessage'
import { useStore } from '../store/useStore'
import { useToast } from '../hooks/useToast'
import { sendChat, getChatHistory } from '../utils/api'

const STARTERS = [
  'Generate a 5-question Python quiz at medium difficulty.',
  'Build me a 6-week study plan for becoming a data scientist.',
  'How should I prepare for a frontend system design interview?',
  'Recommend free courses to learn React.',
]

export default function Chat() {
  const sessionId    = useStore((s) => s.sessionId)
  const setSessionId = useStore((s) => s.setSessionId)
  const toast        = useToast()
  const [messages, setMessages] = useState([])
  const [input, setInput]       = useState('')
  const [loading, setLoading]   = useState(false)
  const endRef = useRef(null)

  useEffect(() => {
    (async () => {
      try {
        const history = await getChatHistory(sessionId)
        if (history?.length) setMessages(history)
      } catch (_) { /* first-time session: ignore */ }
    })()
  }, [sessionId])

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, loading])

  const send = async (textOverride) => {
    const text = (textOverride ?? input).trim()
    if (!text || loading) return
    setInput('')
    setMessages((m) => [...m, { role: 'user', content: text }])
    setLoading(true)
    try {
      const res = await sendChat({ message: text, session_id: sessionId })
      if (res.session_id && res.session_id !== sessionId) setSessionId(res.session_id)
      setMessages((m) => [
        ...m,
        {
          role: 'assistant',
          content: res.reply,
          intent: res.intent,
          eval_score: res.eval_score,
        },
      ])
      if (res.blocked) toast.info('Response blocked by guardrails — try an educational query.')
    } catch (e) {
      toast.error('Sorry, something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const resetChat = () => {
    const id = (crypto.randomUUID && crypto.randomUUID()) || String(Date.now())
    setSessionId(id)
    setMessages([])
    toast.success('Started a new session.')
  }

  return (
    <>
      <PageHeader
        title="AI Chat"
        subtitle="Talk to your career & learning copilot. Education and career topics only."
        icon={MessageSquare}
        actions={
          <button onClick={resetChat} className="btn-secondary">
            <RotateCcw className="w-4 h-4" /> New chat
          </button>
        }
      />

      <GlassCard className="!p-0 overflow-hidden">
        <div className="h-[60vh] sm:h-[65vh] overflow-y-auto p-4 sm:p-6 space-y-4">
          {messages.length === 0 && !loading && (
            <div className="h-full flex flex-col items-center justify-center text-center gap-4">
              <div className="w-14 h-14 rounded-2xl bg-gradient-edu flex items-center justify-center shadow-glow">
                <Sparkles className="w-7 h-7 text-white" />
              </div>
              <div className="font-display font-bold text-xl heading-gradient">How can I help you grow today?</div>
              <div className="text-slate-500 text-sm">Try one of these to get started:</div>
              <div className="grid sm:grid-cols-2 gap-2 max-w-2xl w-full mt-1">
                {STARTERS.map((s) => (
                  <button key={s} onClick={() => send(s)}
                    className="text-left text-sm rounded-xl border border-lavender-200 bg-white/70 hover:bg-white px-4 py-3 transition">
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <ChatMessage key={i} role={m.role} content={m.content} intent={m.intent} eval_score={m.eval_score} />
          ))}
          {loading && <TypingBubble />}
          <div ref={endRef} />
        </div>

        {/* Input area */}
        <div className="border-t border-white/40 p-3 sm:p-4 bg-white/50 backdrop-blur">
          <div className="flex gap-2 items-end">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }}
              rows={1}
              placeholder="Ask about quizzes, study plans, resumes, interviews…"
              className="input-field resize-none min-h-[44px] max-h-32"
            />
            <button onClick={() => send()} disabled={loading || !input.trim()} className="btn-primary !px-4">
              <Send className="w-4 h-4" />
            </button>
          </div>
          <div className="text-[11px] text-slate-400 mt-1.5 pl-1">
            Only educational and career questions are supported. Press <kbd className="px-1.5 py-0.5 rounded bg-slate-100">Enter</kbd> to send.
          </div>
        </div>
      </GlassCard>
    </>
  )
}
