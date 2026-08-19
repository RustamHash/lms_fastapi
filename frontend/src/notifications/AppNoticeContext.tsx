import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import type { ListNoticeKind } from '../components/ListTableShell'

type AppNotice = {
  message: string
  kind: ListNoticeKind
}

type AppNoticeContextValue = {
  notice: AppNotice | null
  notify: (message: string, kind: ListNoticeKind) => void
  clearNotice: () => void
}

const AppNoticeContext = createContext<AppNoticeContextValue | null>(null)

export function AppNoticeProvider({ children }: { children: ReactNode }) {
  const [notice, setNotice] = useState<AppNotice | null>(null)

  const notify = useCallback((message: string, kind: ListNoticeKind) => {
    setNotice({ message, kind })
  }, [])

  const clearNotice = useCallback(() => {
    setNotice(null)
  }, [])

  useEffect(() => {
    if (!notice) return
    const timer = window.setTimeout(() => setNotice(null), 3000)
    return () => window.clearTimeout(timer)
  }, [notice])

  const value = useMemo(
    () => ({
      notice,
      notify,
      clearNotice,
    }),
    [notice, notify, clearNotice],
  )

  return <AppNoticeContext.Provider value={value}>{children}</AppNoticeContext.Provider>
}

export function useAppNotice(): AppNoticeContextValue {
  const ctx = useContext(AppNoticeContext)
  if (!ctx) throw new Error('useAppNotice вне AppNoticeProvider')
  return ctx
}
