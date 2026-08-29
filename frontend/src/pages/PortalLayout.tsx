import { Link, Outlet, Navigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export function PortalLayout() {
  const { user, logout, loading } = useAuth()

  if (loading) {
    return <div className="app-main"><p className="app-card">Загрузка...</p></div>
  }
  if (!user) {
    return <Navigate to="/login" replace />
  }
  if (!user.is_portal_user) {
    return <Navigate to="/" replace />
  }

  return (
    <div className="portal-shell">
      <header className="portal-header">
        <div className="portal-brand">Портал поклажедателя</div>
        <nav className="portal-nav">
          <Link to="/portal">Сводка</Link>
          <Link to="/portal/products">Товары</Link>
          <Link to="/portal/orders">Заказы</Link>
          <Link to="/portal/stock">Остатки</Link>
        </nav>
        <div className="portal-user">
          <span>{user.username}</span>
          <button type="button" onClick={logout}>Выйти</button>
        </div>
      </header>
      <main className="portal-main">
        <Outlet />
      </main>
    </div>
  )
}
