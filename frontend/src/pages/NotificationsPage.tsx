import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-list/EntityListPage'
import { notificationsConfig } from '../features/notifications/config'

export function NotificationsPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={notificationsConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Главная', to: '/' },
        { label: 'Уведомления' },
      ]}
    />
  )
}
