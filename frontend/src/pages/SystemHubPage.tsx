import { HubPage } from '../components/HubPage'

export function SystemHubPage() {
  return (
    <HubPage
      title="Система"
      subtitle="Управление системой"
      breadcrumbs={[{ label: 'Главная', to: '/' }, { label: 'Система' }]}
      sections={[
        {
          title: 'Пользователи и доступ',
          icon: '🔐',
          items: [
            { to: '/users', label: 'Пользователи', description: 'Учётные записи', icon: '👤' },
            { to: '/roles', label: 'Роли', description: 'Роли и права', icon: '🔑' },
          ],
        },
        {
          title: 'Мониторинг',
          icon: '📊',
          items: [
            { to: '/audit', label: 'Аудит', description: 'Журнал действий', icon: '📋' },
            { to: '/notifications', label: 'Уведомления', description: 'Уведомления системы', icon: '🔔' },
            { to: '/notification-rules', label: 'Правила уведомлений', description: 'Настройка правил', icon: '📏' },
          ],
        },
      ]}
    />
  )
}
