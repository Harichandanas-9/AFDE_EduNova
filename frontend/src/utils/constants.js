import {
  LayoutDashboard,
  MessageSquare,
  BookOpenCheck,
  CalendarRange,
  FileText,
  Target,
  Sparkles,
  BarChart3,
  Settings,
} from 'lucide-react'

export const NAV_ITEMS = [
  { name: 'Dashboard',         path: '/',                  icon: LayoutDashboard, color: 'text-sea-600' },
  { name: 'AI Chat',           path: '/chat',              icon: MessageSquare,    color: 'text-lavender-600' },
  { name: 'Quiz Generator',    path: '/quiz',              icon: BookOpenCheck,    color: 'text-mint-600' },
  { name: 'Study Planner',     path: '/study-planner',     icon: CalendarRange,    color: 'text-sea-600' },
  { name: 'Resume Builder',    path: '/resume',            icon: FileText,         color: 'text-blush-600' },
  { name: 'Skill Gap Analyzer',path: '/skill-gap',         icon: Target,           color: 'text-lavender-600' },
  { name: 'Recommendations',   path: '/recommendations',   icon: Sparkles,         color: 'text-mint-600' },
  { name: 'Analytics',         path: '/analytics',         icon: BarChart3,        color: 'text-sea-600' },
  { name: 'Settings',          path: '/settings',          icon: Settings,         color: 'text-slate-600' },
]

export const STORAGE_KEYS = {
  session: 'edunova_session_id',
  user: 'edunova_user',
}
