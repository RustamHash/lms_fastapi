import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-list/EntityListPage'
import { routesConfig } from '../features/routes/config'

export function RoutesPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={routesConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Доставка', to: '/' },
        { label: 'Маршруты' },
      ]}
    />
  )
}
