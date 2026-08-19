import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-list/EntityListPage'
import { vehiclesConfig } from '../features/vehicles/config'

export function VehiclesPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={vehiclesConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Доставка', to: '/' },
        { label: 'Транспорт' },
      ]}
    />
  )
}
