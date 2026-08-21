import { memo, useEffect, useRef, useState } from 'react'
import { NavLink, Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

type MenuGroup = {
  label: string
  to?: string
  items?: {
    to: string
    label: string
  }[]
}

const MENU_GROUPS: MenuGroup[] = [
  {
    label: 'Главная',
    to: '/',
  },
  {
    label: 'Справочники',
    to: '/references',
    items: [
      { to: '/reference/addresses', label: 'Адреса' },
      { to: '/reference/clients', label: 'Клиенты' },
      { to: '/reference/products', label: 'Товары' },
      { to: '/reference/contracts', label: 'Договоры' },
    ],
  },
  {
    label: 'Склад',
    to: '/stock',
    items: [
      { to: '/reference/products', label: 'Товары' },
      { to: '/stock', label: 'Остатки' },
      { to: '/tasks', label: 'Задания' },
      { to: '/topology/locations', label: 'Ячейки' },
    ],
  },
  {
    label: 'Заказы',
    to: '/orders',
    items: [
      { to: '/orders/inbound', label: 'Входящие' },
      { to: '/orders/outbound', label: 'Исходящие' },
      { to: '/orders/return', label: 'Возвратные' },
    ],
  },
  {
    label: 'Документы',
    to: '/documents',
  },
  {
    label: 'Доставка',
    to: '/delivery/orders',
    items: [
      { to: '/delivery/orders', label: 'Заказы' },
      { to: '/reference/drivers', label: 'Водители' },
      { to: '/reference/routes', label: 'Маршруты' },
      { to: '/reference/vehicles', label: 'Транспорт' },
    ],
  },
  {
    label: 'Система',
    to: '/users',
    items: [
      { to: '/notifications', label: 'Уведомления' },
      { to: '/users', label: 'Пользователи' },
      { to: '/roles', label: 'Роли' },
      { to: '/audit', label: 'Аудит' },
    ],
  },
  {
    label: 'Интеграции',
    to: '/integrations/profiles',
    items: [
      { to: '/integrations/profiles', label: 'Профили' },
      { to: '/integrations/logs', label: 'Логи' },
    ],
  },
  {
    label: 'Файлы',
    to: '/files',
  },
]

function NavbarInner() {
  const { user, logout } = useAuth()
  const [openGroup, setOpenGroup] = useState<string | null>(null)
  const navRef = useRef<HTMLElement>(null)

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (navRef.current && !navRef.current.contains(e.target as Node)) {
        setOpenGroup(null)
      }
    }
    document.addEventListener('click', handler)
    return () => document.removeEventListener('click', handler)
  }, [])

  function getSectionTitle(label: string): string {
    const titles: Record<string, string> = {
      'Справочники': 'Все справочники',
      'Склад': 'Обзор склада',
      'Доставка': 'Обзор доставки',
      'Система': 'Обзор системы',
      'Интеграции': 'Все интеграции',
    }
    return titles[label] ?? label
  }

  return (
    <nav className="app-navbar" ref={navRef}>
      <div className="app-navbar__inner">
        <ul className="app-menu app-menu--main">
          {MENU_GROUPS.map((group) => {
            // Простой пункт без подменю
            if (!group.items || group.items.length === 0) {
              return (
                <li key={group.label}>
                  <NavLink to={group.to!} end>
                    {group.label}
                  </NavLink>
                </li>
              )
            }
            
            // Группа с подменю
            return (
              <li key={group.label} className="app-menu__group">
                <button
                  type="button"
                  className="app-menu__trigger"
                  onClick={(e) => {
                    e.stopPropagation()
                    setOpenGroup(openGroup === group.label ? null : group.label)
                  }}
                  aria-expanded={openGroup === group.label}
                >
                  {group.label}
                  <span className="app-menu__arrow" aria-hidden>▾</span>
                </button>
                
                {openGroup === group.label ? (
                  <ul className="app-menu__dropdown" role="menu">
                    {/* Первая строка — ссылка на весь раздел */}
                    <li role="none" className="app-menu__dropdown-all">
                      <Link
                        to={group.to!}
                        role="menuitem"
                        onClick={() => setOpenGroup(null)}
                      >
                        {getSectionTitle(group.label)} →
                      </Link>
                    </li>
                    
                    {/* Разделитель */}
                    <li className="app-menu__divider" role="separator" />
                    
                    {/* Часто используемые пункты */}
                    {group.items.map((item) => (
                      <li key={item.to} role="none">
                        <NavLink
                          to={item.to}
                          role="menuitem"
                          onClick={() => setOpenGroup(null)}
                        >
                          {item.label}
                        </NavLink>
                      </li>
                    ))}
                  </ul>
                ) : null}
              </li>
            )
          })}
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
