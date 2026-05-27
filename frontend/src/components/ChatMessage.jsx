import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { motion } from 'framer-motion'
import { Bot, User } from 'lucide-react'
import clsx from 'clsx'

export default function ChatMessage({ role, content, eval_score, intent }) {
  const isUser = role === 'user'
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={clsx('flex gap-3', isUser ? 'justify-end' : 'justify-start')}
    >
      {!isUser && (
        <div className="w-9 h-9 rounded-xl bg-gradient-edu flex items-center justify-center shrink-0 shadow-glow">
          <Bot className="w-5 h-5 text-white" />
        </div>
      )}
      <div
        className={clsx(
          'max-w-[80%] sm:max-w-[70%] rounded-2xl px-4 py-3 shadow-glass border',
          isUser
            ? 'bg-gradient-edu text-white border-transparent rounded-tr-sm'
            : 'glass text-slate-800 rounded-tl-sm',
        )}
      >
        <div className="prose-chat text-[0.95rem]">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '')
                if (!inline && match) {
                  return (
                    <SyntaxHighlighter style={oneDark} language={match[1]} PreTag="div" {...props}>
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  )
                }
                return <code className={className} {...props}>{children}</code>
              },
            }}
          >
            {content || ''}
          </ReactMarkdown>
        </div>
        {!isUser && (intent || eval_score != null) && (
          <div className="mt-2 flex gap-2 text-[10px] uppercase tracking-wider opacity-70">
            {intent && <span className="chip !py-0.5 !text-[10px]">intent: {intent}</span>}
            {eval_score != null && (
              <span className="chip !py-0.5 !text-[10px] !bg-mint-100 !text-mint-700 !border-mint-200">
                eval: {Math.round(eval_score * 100)}%
              </span>
            )}
          </div>
        )}
      </div>
      {isUser && (
        <div className="w-9 h-9 rounded-xl bg-white/70 backdrop-blur border border-lavender-200 flex items-center justify-center shrink-0">
          <User className="w-5 h-5 text-lavender-700" />
        </div>
      )}
    </motion.div>
  )
}

export function TypingBubble() {
  return (
    <div className="flex gap-3 items-end">
      <div className="w-9 h-9 rounded-xl bg-gradient-edu flex items-center justify-center shadow-glow">
        <Bot className="w-5 h-5 text-white" />
      </div>
      <div className="glass rounded-2xl px-4 py-3 flex gap-1 items-center">
        <span className="w-2 h-2 rounded-full bg-lavender-500 animate-pulse-soft" />
        <span className="w-2 h-2 rounded-full bg-lavender-500 animate-pulse-soft [animation-delay:.2s]" />
        <span className="w-2 h-2 rounded-full bg-lavender-500 animate-pulse-soft [animation-delay:.4s]" />
      </div>
    </div>
  )
}
