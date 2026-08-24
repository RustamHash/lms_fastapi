import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { apiClient } from '../lib/apiClient'
import { getAccessToken, setAccessToken } from '../lib/token'

export type AuthUser = { id: number; username: string; is_superuser?: boolean; permissions?: Record<string, string[] | boolean> }

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
      // Отложить setState через microtask
      Promise.resolve().then(() => setLoading(false))
      return
    }
    let cancelled = false
    apiClient.get<AuthUser>('/api/v1/auth/me')
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
    const me = await apiClient.get<AuthUser>('/api/v1/auth/me')
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


/** Проверка: есть ли у пользователя все права */
export function hasFullAccess(user: AuthUser | null): boolean {
  if (!user) return false
  if (user.is_superuser) return true
  const all = user.permissions?.all
  if (typeof all === 'boolean') return all
  if (Array.isArray(all)) return all.includes('all')
  return false
}

/** Проверка конкретного права */
export function hasPermission(
  user: AuthUser | null,
  module: string,
  action: string,
): boolean {
  if (!user) return false
  if (user.is_superuser) return true
  if (hasFullAccess(user)) return true
  const perms = user.permissions?.[module]
  if (typeof perms === 'boolean') return perms
  if (Array.isArray(perms)) return perms.includes(action)
  return false
}

/** Проверка доступа к модулю (любое право) */
export function hasModuleAccess(
  user: AuthUser | null,
  module: string,
): boolean {
  if (!user) return false
  if (user.is_superuser) return true
  if (hasFullAccess(user)) return true
  const perms = user.permissions?.[module]
  if (typeof perms === 'boolean') return perms
  if (Array.isArray(perms)) return perms.length > 0
  return false
}

/** Получить список прав пользователя на модуль */
export function getModulePermissions(
  user: AuthUser | null,
  module: string,
): string[] {
  if (!user) return []
  if (user.is_superuser || hasFullAccess(user)) {
    return ['view', 'create', 'update', 'delete', 'execute', 'complete', 'approve', 'cancel']
  }
  const perms = user.permissions?.[module]
  if (Array.isArray(perms)) return perms
  return []
}

/** Получить текст с описанием отсутствующего права */
export function getPermissionMessage(
  user: AuthUser | null,
  module: string,
  action: string,
): string {
  const userPerms = getModulePermissions(user, module)
  return `Нужно право: ${action}. Ваши права: ${userPerms.length > 0 ? userPerms.join(', ') : 'нет'}`
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth вне AuthProvider')
  return ctx
}
