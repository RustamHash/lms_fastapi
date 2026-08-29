import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

/** Операторский UI: portal-пользователей уводим в /portal. */
export function RequireOperator() {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="app-main">
        <p className="app-card">Загрузка…</p>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  if (user.is_portal_user) {
    return <Navigate to="/portal" replace />
  }

  return <Outlet />
}
