import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { routesConfig } from '../features/routes/config'

export function RoutesPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={routesConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Справочники', to: '/references' },
        { label: 'Маршруты' },
      ]}
    />
  )
}
