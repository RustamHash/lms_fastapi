import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { apiFetch } from '../lib/http'
import { getAccessToken, setAccessToken } from '../lib/token'

export type AuthUser = { id: number; username: string; permissions?: Record<string, string[] | boolean> }

type AuthContextValue = {
  user: AuthUser | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  register: (username: string, password: string) => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const t = getAccessToken()
    if (!t) {
      setLoading(false)
      return
    }
    let cancelled = false
    apiFetch('/api/v1/auth/me')
      .then((r) => {
        if (!r.ok) throw new Error('me')
        return r.json() as Promise<AuthUser>
      })
      .then((u) => {
        if (!cancelled) setUser(u)
      })
      .catch(() => {
        setAccessToken(null)
        if (!cancelled) setUser(null)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const login = useCallback(async (username: string, password: string) => {
    const body = new URLSearchParams()
    body.set('username', username)
    body.set('password', password)
    const res = await fetch('/api/v1/auth/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body,
    })
    if (!res.ok) throw new Error('Неверные учётные данные')
    const data = (await res.json()) as { access_token: string }
    setAccessToken(data.access_token)
    const me = await apiFetch('/api/v1/auth/me').then((r) => {
      if (!r.ok) throw new Error('me')
      return r.json() as Promise<AuthUser>
    })
    setUser(me)
  }, [])

  const register = useCallback(
    async (username: string, password: string) => {
      const res = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
      if (!res.ok) {
        const t = await res.text()
        throw new Error(t || 'Ошибка регистрации')
      }
      await login(username, password)
    },
    [login],
  )

  const logout = useCallback(() => {
    setAccessToken(null)
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, loading, login, logout, register }),
    [user, loading, login, logout, register],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth вне AuthProvider')
  return ctx
}
