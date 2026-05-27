import { useStore } from '../store/useStore'

export const useToast = () => {
  const pushToast = useStore((s) => s.pushToast)
  return {
    success: (message, opts = {}) => pushToast({ type: 'success', message, ...opts }),
    error:   (message, opts = {}) => pushToast({ type: 'error',   message, ...opts }),
    info:    (message, opts = {}) => pushToast({ type: 'info',    message, ...opts }),
  }
}
