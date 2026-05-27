import { motion } from 'framer-motion'
import clsx from 'clsx'

export default function GlassCard({ children, className, hover = true, delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay, ease: 'easeOut' }}
      whileHover={hover ? { y: -3 } : undefined}
      className={clsx(
        'glass p-5 sm:p-6 transition-shadow duration-300',
        hover && 'hover:shadow-glow-mint',
        className,
      )}
    >
      {children}
    </motion.div>
  )
}
