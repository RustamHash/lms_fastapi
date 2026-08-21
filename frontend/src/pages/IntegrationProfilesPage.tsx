import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { integrationProfilesConfig } from '../features/integration-profiles/config'

export function IntegrationProfilesPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={integrationProfilesConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Главная', to: '/' },
        { label: 'Профили' },
      ]}
    />
  )
}
