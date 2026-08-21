import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

type Tab = {
  path: string
  label: string
}

type TabsContextValue = {
  tabs: Tab[]
  activePath: string
  closeTab: (path: string) => void
  closeAllTabs: () => void
}

const TabsContext = createContext<TabsContextValue | null>(null)

const STORAGE_KEY = 'sslogistics_tabs'
const MAX_TABS = 5

// Маппинг путей к названиям
function getLabelFromPath(path: string): string {
  const map: Record<string, string> = {
    '/': 'Главная',
    '/references': 'Справочники',
    '/documents': 'Документы',
    '/documents-hub': 'Документы',
    '/tasks': 'Задания',
    '/stock': 'Остатки',
    '/orders': 'Заказы',
    '/orders/inbound': 'Входящие',
    '/orders/outbound': 'Исходящие',
    '/orders/return': 'Возвратные',
    '/users': 'Пользователи',
    '/roles': 'Роли',
    '/audit': 'Аудит',
    '/notifications': 'Уведомления',
    '/notification-rules': 'Правила',
    '/files': 'Файлы',
    '/carriers': 'Перевозчики',
    '/keepers': 'Хранители',
    '/deviations': 'Отклонения',
    '/route-lines': 'Маршруты',
    '/delivery': 'Доставка',
    '/delivery/orders': 'Заказы доставки',
    '/warehouse': 'Склад',
    '/system': 'Система',
    '/integrations': 'Интеграции',
    '/integrations/profiles': 'Профили',
    '/integrations/logs': 'Логи',
  }

  // Проверяем точное совпадение
  if (map[path]) return map[path]

  // Проверяем префиксы
  for (const [key, value] of Object.entries(map)) {
    if (path.startsWith(key + '/') || path === key) {
      return value
    }
  }

  // Для справочников
  const refMap: Record<string, string> = {
    '/reference/addresses': 'Адреса',
    '/reference/address-input-aliases': 'Варианты ввода',
    '/reference/delivery-zones': 'Зоны',
    '/reference/legal-entities': 'Юрлица',
    '/reference/depositors': 'Поклажедатели',
    '/reference/clients': 'Клиенты',
    '/reference/trade-points': 'ТТ',
    '/reference/contracts': 'Договоры',
    '/reference/tariffs': 'Тарифы',
    '/reference/tariff-documents': 'Тарифы док.',
    '/reference/products': 'Товары',
    '/reference/batches': 'Партии',
    '/reference/lpns': 'LPN',
    '/reference/drivers': 'Водители',
    '/reference/vehicles': 'Транспорт',
    '/reference/routes': 'Маршруты',
    '/topology/warehouses': 'Склады',
    '/topology/virtual-warehouses': 'Вирт. склады',
    '/topology/zones': 'Зоны',
    '/topology/rows': 'Ряды',
    '/topology/locations': 'Ячейки',
  }

  for (const [key, value] of Object.entries(refMap)) {
    if (path.startsWith(key)) {
      return value
    }
  }

  return path.split('/').filter(Boolean).pop() || 'Страница'
}

export function TabsProvider({ children }: { children: ReactNode }) {
  const location = useLocation()
  const navigate = useNavigate()
  const [tabs, setTabs] = useState<Tab[]>(() => {
    try {
      const saved = sessionStorage.getItem(STORAGE_KEY)
      if (saved) {
        const parsed = JSON.parse(saved) as Tab[]
        return parsed.slice(0, MAX_TABS)
      }
    } catch {
      // ignore
    }
    return []
  })

  const activePath = location.pathname

  // Пути, которые НЕ должны быть табами (главная и hub-страницы)
  const EXCLUDED_PATHS = [
    '/',
    '/login',
    '/references',
    '/documents-hub',
    '/orders',
    '/warehouse',
    '/delivery',
    '/system',
    '/integrations',
  ]

  // Добавляем текущую страницу в табы
  useEffect(() => {
    if (activePath === '/login') return
    
    // Проверяем, не является ли путь исключённым
    if (EXCLUDED_PATHS.includes(activePath)) return
    
    // Проверяем точное совпадение с hub-страницами
    for (const excluded of EXCLUDED_PATHS) {
      if (activePath === excluded) return
    }

    setTabs((prev) => {
      // Если таб уже есть — обновляем label
      const existing = prev.find((t) => t.path === activePath)
      if (existing) {
        return prev.map((t) => 
          t.path === activePath ? { ...t, label: getLabelFromPath(activePath) } : t
        )
      }

      // Добавляем новый таб
      const newTab: Tab = {
        path: activePath,
        label: getLabelFromPath(activePath),
      }
      const next = [...prev, newTab]
      return next.slice(-MAX_TABS)
    })
  }, [activePath])

  // Сохраняем в sessionStorage
  useEffect(() => {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(tabs))
    } catch {
      // ignore
    }
  }, [tabs])

  const closeTab = useCallback((path: string) => {
    setTabs((prev) => {
      const next = prev.filter((t) => t.path !== path)
      
      // Если закрыли активный таб — переходим на последний
      if (path === activePath && next.length > 0) {
        navigate(next[next.length - 1].path)
      }
      
      return next
    })
  }, [activePath, navigate])

  const closeAllTabs = useCallback(() => {
    setTabs([])
    navigate('/')
  }, [navigate])

  const value = useMemo(
    () => ({ tabs, activePath, closeTab, closeAllTabs }),
    [tabs, activePath, closeTab, closeAllTabs],
  )

  return <TabsContext.Provider value={value}>{children}</TabsContext.Provider>
}

export function useTabs(): TabsContextValue {
  const ctx = useContext(TabsContext)
  if (!ctx) throw new Error('useTabs вне TabsProvider')
  return ctx
}
