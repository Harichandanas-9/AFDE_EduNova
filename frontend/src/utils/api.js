import axios from 'axios'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || '/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60_000,
  headers: { 'Content-Type': 'application/json' },
})

// Lightweight retry on 5xx / network errors
api.interceptors.response.use(
  (r) => r,
  async (error) => {
    const cfg = error.config || {}
    cfg.__retry = (cfg.__retry || 0) + 1
    const status = error.response?.status
    if (cfg.__retry <= 1 && (!status || status >= 500)) {
      await new Promise((r) => setTimeout(r, 600))
      return api(cfg)
    }
    return Promise.reject(error)
  },
)

// --- Chat ---
export const sendChat = (payload) => api.post('/chat', payload).then((r) => r.data)
export const getChatHistory = (sessionId) =>
  api.get(`/chat/history/${sessionId}`).then((r) => r.data)

// --- Quiz ---
export const generateQuiz = (payload) => api.post('/quiz/generate', payload).then((r) => r.data)
export const submitQuiz = (payload) => api.post('/quiz/submit', payload).then((r) => r.data)
export const recentQuizzes = () => api.get('/quiz/recent').then((r) => r.data)
export const recentQuizResults = () => api.get('/quiz/results/recent').then((r) => r.data)

// --- Study plan ---
export const createStudyPlan = (payload) => api.post('/study-plan', payload).then((r) => r.data)
export const getStudyPlan = (id) => api.get(`/study-plan/${id}`).then((r) => r.data)
export const listStudyPlans = () => api.get('/study-plan').then((r) => r.data)

// --- Resume ---
export const buildResume = (payload) => api.post('/resume/build', payload).then((r) => r.data)
export const getResume = (id) => api.get(`/resume/${id}`).then((r) => r.data)

// --- Skill / recommendations ---
export const analyzeSkillGap = (payload) => api.post('/skill-gap', payload).then((r) => r.data)
export const getRecommendations = (payload) =>
  api.post('/recommendations', payload).then((r) => r.data)

// --- Health ---
export const health = () => api.get('/health').then((r) => r.data)

export default api
