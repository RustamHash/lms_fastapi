import { memo } from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

function NavbarInner() {
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
            <NavLink to="/tasks">Задания</NavLink>
          </li>
          <li>
            <NavLink to="/documents">Документы</NavLink>
          </li>
          <li>
            <NavLink to="/delivery/orders">Доставка</NavLink>
          </li>
          <li>
            <NavLink to="/audit">Аудит</NavLink>
          </li>
          <li>
            <NavLink to="/notification-rules">Правила</NavLink>
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
            <NavLink to="/carriers">Перевозчики</NavLink>
          </li>
          <li>
            <NavLink to="/keepers">Хранители</NavLink>
          </li>
          <li>
            <NavLink to="/deviations">Отклонения</NavLink>
          </li>
          <li>
            <NavLink to="/stock">Остатки</NavLink>
          </li>
          <li>
            <NavLink to="/topology/warehouses">Топология</NavLink>
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


export const Navbar = memo(NavbarInner)
