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

type AppNoticeStateContextValue = {
  notice: AppNotice | null
}

type AppNoticeActionsContextValue = {
  notify: (message: string, kind: ListNoticeKind) => void
  clearNotice: () => void
}

const AppNoticeStateContext = createContext<AppNoticeStateContextValue | null>(null)
const AppNoticeActionsContext = createContext<AppNoticeActionsContextValue | null>(null)

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

  const stateValue = useMemo(
    () => ({ notice }),
    [notice],
  )

  const actionsValue = useMemo(
    () => ({ notify, clearNotice }),
    [notify, clearNotice],
  )

  return (
    <AppNoticeStateContext.Provider value={stateValue}>
      <AppNoticeActionsContext.Provider value={actionsValue}>
        {children}
      </AppNoticeActionsContext.Provider>
    </AppNoticeStateContext.Provider>
  )
}

export function useAppNoticeState(): AppNoticeStateContextValue {
  const ctx = useContext(AppNoticeStateContext)
  if (!ctx) throw new Error('useAppNoticeState вне AppNoticeProvider')
  return ctx
}

export function useAppNoticeActions(): AppNoticeActionsContextValue {
  const ctx = useContext(AppNoticeActionsContext)
  if (!ctx) throw new Error('useAppNoticeActions вне AppNoticeProvider')
  return ctx
}

// Обратная совместимость
export function useAppNotice() {
  const state = useAppNoticeState()
  const actions = useAppNoticeActions()
  return { ...state, ...actions }
}
