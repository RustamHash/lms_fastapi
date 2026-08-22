import { HubPage } from '../components/HubPage'

export function IntegrationsHubPage() {
  return (
    <HubPage
      title="Интеграции"
      subtitle="Обмен данными с внешними системами"
      breadcrumbs={[{ label: 'Главная', to: '/' }, { label: 'Интеграции' }]}
      sections={[
        {
          title: 'Интеграция',
          icon: '🔌',
          items: [
            { to: '/integrations/profiles', label: 'Профили', description: 'Профили интеграций', icon: '⚙️' },
            { to: '/integrations/logs', label: 'Логи', description: 'Логи обмена', icon: '📋' },
          ],
        },
      ]}
    />
  )
}
