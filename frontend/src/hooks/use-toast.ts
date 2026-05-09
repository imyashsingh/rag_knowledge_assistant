import { useState, useCallback } from 'react'

interface Toast {
  id: string
  title?: string
  description?: string
  action?: React.ReactNode
}

interface ToastState {
  toasts: Toast[]
}

export function useToast() {
  const [state, setState] = useState<ToastState>({ toasts: [] })

  const toast = useCallback(({ title, description, action }: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9)
    setState((prev) => ({
      toasts: [...prev.toasts, { id, title, description, action }]
    }))
  }, [])

  const dismiss = useCallback((id: string) => {
    setState((prev) => ({
      toasts: prev.toasts.filter((toast) => toast.id !== id)
    }))
  }, [])

  return {
    ...state,
    toast,
    dismiss,
  }
}
