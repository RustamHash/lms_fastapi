import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { integrationLogsConfig } from '../features/integration-logs/config'

export function IntegrationLogsPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={integrationLogsConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Главная', to: '/' },
        { label: 'Логи' },
      ]}
    />
  )
}
