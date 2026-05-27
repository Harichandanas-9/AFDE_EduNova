import { NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import { GraduationCap, ChevronLeft, ChevronRight } from 'lucide-react'
import clsx from 'clsx'
import { NAV_ITEMS } from '../utils/constants'
import { useStore } from '../store/useStore'

export default function Sidebar() {
  const open = useStore((s) => s.sidebarOpen)
  const toggle = useStore((s) => s.toggleSidebar)

  return (
    <motion.aside
      animate={{ width: open ? 248 : 84 }}
      transition={{ type: 'spring', stiffness: 220, damping: 26 }}
      className="hidden md:flex shrink-0 z-30 sticky top-0 h-screen p-3"
    >
      <div className="glass-strong flex flex-col h-full w-full p-4 overflow-hidden">
        {/* Brand */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-edu flex items-center justify-center shadow-glow">
            <GraduationCap className="w-5 h-5 text-white" />
          </div>
          {open && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="leading-tight">
              <div className="font-display font-extrabold text-lg heading-gradient">EduNova</div>
              <div className="text-[10px] uppercase tracking-widest text-slate-500">AI Copilot</div>
            </motion.div>
          )}
        </div>

        {/* Nav */}
        <nav className="flex-1 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === '/'}
                className={({ isActive }) => clsx(
                  'group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition',
                  isActive
                    ? 'bg-gradient-edu text-white shadow-glow'
                    : 'text-slate-600 hover:bg-white/70 hover:text-sea-700',
                )}
              >
                <Icon className={clsx('w-5 h-5 shrink-0 transition group-hover:scale-110')} />
                {open && (
                  <motion.span initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }}>
                    {item.name}
                  </motion.span>
                )}
              </NavLink>
            )
          })}
        </nav>

        {/* Collapse toggle */}
        <button
          onClick={toggle}
          className="mt-3 flex items-center justify-center gap-2 text-xs text-slate-500 hover:text-sea-700 transition"
        >
          {open ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          {open && <span>Collapse</span>}
        </button>
      </div>
    </motion.aside>
  )
}
