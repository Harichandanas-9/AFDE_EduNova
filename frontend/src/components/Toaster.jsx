import { AnimatePresence, motion } from 'framer-motion'
import { CheckCircle2, AlertTriangle, Info, X } from 'lucide-react'
import { useStore } from '../store/useStore'

const ICONS = {
  success: <CheckCircle2 className="w-5 h-5 text-mint-600" />,
  error:   <AlertTriangle className="w-5 h-5 text-blush-600" />,
  info:    <Info className="w-5 h-5 text-sea-600" />,
}

export default function Toaster() {
  const toasts = useStore((s) => s.toasts)
  const dismiss = useStore((s) => s.dismissToast)
  return (
    <div className="fixed z-[60] bottom-4 right-4 flex flex-col gap-2 max-w-sm w-[92vw] sm:w-96">
      <AnimatePresence>
        {toasts.map((t) => (
          <motion.div
            key={t.id}
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0,  scale: 1 }}
            exit={{    opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="glass-strong flex items-start gap-3 px-4 py-3"
          >
            {ICONS[t.type] || ICONS.info}
            <div className="flex-1 text-sm text-slate-700">{t.message}</div>
            <button onClick={() => dismiss(t.id)} className="text-slate-400 hover:text-slate-700">
              <X className="w-4 h-4" />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
