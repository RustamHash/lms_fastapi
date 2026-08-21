import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { notificationRulesConfig } from '../features/notification-rules/config'

export function NotificationRulesPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={notificationRulesConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Главная', to: '/' },
        { label: 'Правила уведомлений' },
      ]}
    />
  )
}
