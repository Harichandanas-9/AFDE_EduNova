import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { Menu, X, GraduationCap } from 'lucide-react'
import { NAV_ITEMS } from '../utils/constants'
import clsx from 'clsx'

export default function MobileNav() {
  const [open, setOpen] = useState(false)
  return (
    <div className="md:hidden">
      <div className="flex items-center justify-between p-3">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-lg bg-gradient-edu flex items-center justify-center shadow-glow">
            <GraduationCap className="w-5 h-5 text-white" />
          </div>
          <div className="font-display font-extrabold heading-gradient">EduNova</div>
        </div>
        <button onClick={() => setOpen(true)} className="glass p-2"><Menu className="w-5 h-5" /></button>
      </div>
      <AnimatePresence>
        {open && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/30 backdrop-blur-sm">
            <motion.div initial={{ x: '-100%' }} animate={{ x: 0 }} exit={{ x: '-100%' }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className="absolute left-0 top-0 bottom-0 w-72 p-3">
              <div className="glass-strong h-full p-4 flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <div className="font-display font-extrabold heading-gradient">EduNova</div>
                  <button onClick={() => setOpen(false)} className="p-1.5 rounded-md hover:bg-slate-100"><X className="w-4 h-4" /></button>
                </div>
                <nav className="space-y-1">
                  {NAV_ITEMS.map((item) => {
                    const Icon = item.icon
                    return (
                      <NavLink key={item.path} to={item.path} end={item.path === '/'} onClick={() => setOpen(false)}
                        className={({ isActive }) => clsx(
                          'flex items-center gap-3 px-3 py-2 rounded-xl text-sm',
                          isActive ? 'bg-gradient-edu text-white' : 'text-slate-700 hover:bg-white/70'
                        )}>
                        <Icon className="w-5 h-5" /> {item.name}
                      </NavLink>
                    )
                  })}
                </nav>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
