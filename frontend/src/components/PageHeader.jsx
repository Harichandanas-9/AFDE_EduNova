import { motion } from 'framer-motion'

export default function PageHeader({ title, subtitle, icon: Icon, actions }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6"
    >
      <div className="flex items-center gap-4">
        {Icon && (
          <div className="w-12 h-12 rounded-xl bg-gradient-edu flex items-center justify-center shadow-glow">
            <Icon className="w-6 h-6 text-white" />
          </div>
        )}
        <div>
          <h1 className="font-display text-2xl sm:text-3xl font-extrabold heading-gradient">{title}</h1>
          {subtitle && <p className="text-slate-500 mt-0.5 text-sm sm:text-base">{subtitle}</p>}
        </div>
      </div>
      {actions && <div className="flex gap-2 flex-wrap">{actions}</div>}
    </motion.div>
  )
}
