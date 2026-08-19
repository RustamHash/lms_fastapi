import { NavLink } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export function Navbar() {
  const { user, logout } = useAuth()

  return (
    <nav className="app-navbar">
      <div className="app-navbar__inner">
        <ul className="app-menu app-menu--main">
          <li>
            <NavLink to="/" end>
              Главная
            </NavLink>
          </li>
          <li>
            <NavLink to="/references">Справочники</NavLink>
          </li>
          <li>
            <NavLink to="/warehouse/tasks">Задания</NavLink>
          </li>
          <li>
            <NavLink to="/documents">Документы</NavLink>
          </li>
          <li>
            <NavLink to="/delivery/orders">Доставка</NavLink>
          </li>
          <li>
            <NavLink to="/notifications">Уведомления</NavLink>
          </li>
          <li>
            <NavLink to="/users">Пользователи</NavLink>
          </li>
          <li>
            <NavLink to="/integrations/profiles">Интеграции</NavLink>
          </li>
          <li>
            <NavLink to="/files">Файлы</NavLink>
          </li>
        </ul>
        {user ? (
          <details className="app-user-menu">
            <summary className="app-user-menu__trigger">{user.username}</summary>
            <div className="app-user-menu__panel">
              <a href="/docs" className="app-user-menu__logout">
                API Документация
              </a>
              <button type="button" className="app-user-menu__logout" onClick={() => logout()}>
                Выйти
              </button>
            </div>
          </details>
        ) : null}
      </div>
    </nav>
  )
}
