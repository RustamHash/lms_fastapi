import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-list/EntityListPage'
import { integrationLogsConfig } from '../features/integration-logs/config'

export function IntegrationLogsPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={integrationLogsConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Интеграции', to: '/' },
        { label: 'Логи' },
      ]}
    />
  )
}
