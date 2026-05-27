import { create } from 'zustand'
import { STORAGE_KEYS } from '../utils/constants'

const safeGet = (k, fallback) => {
  try { return JSON.parse(localStorage.getItem(k)) ?? fallback } catch { return fallback }
}
const safeSet = (k, v) => {
  try { localStorage.setItem(k, JSON.stringify(v)) } catch {}
}

const randomId = () =>
  (typeof crypto !== 'undefined' && crypto.randomUUID)
    ? crypto.randomUUID()
    : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,(c)=>{const r=Math.random()*16|0;const v=c==='x'?r:(r&0x3)|0x8;return v.toString(16)})

export const useStore = create((set, get) => ({
  // Session
  sessionId: safeGet(STORAGE_KEYS.session, null) || (() => {
    const id = randomId()
    safeSet(STORAGE_KEYS.session, id)
    return id
  })(),
  setSessionId: (id) => { safeSet(STORAGE_KEYS.session, id); set({ sessionId: id }) },

  // Sidebar
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebarOpen: (v) => set({ sidebarOpen: v }),

  // Toast
  toasts: [],
  pushToast: (toast) => {
    const id = randomId()
    set((s) => ({ toasts: [...s.toasts, { id, ...toast }] }))
    setTimeout(() => get().dismissToast(id), toast.duration || 3500)
  },
  dismissToast: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),

  // Latest analytics snapshot
  analytics: { quizzes: 0, avgScore: 0, plans: 0, resumes: 0 },
  setAnalytics: (a) => set({ analytics: a }),
}))
