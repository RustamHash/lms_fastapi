import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { vehiclesConfig } from '../features/vehicles/config'

export function VehiclesPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={vehiclesConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Справочники', to: '/references' },
        { label: 'Транспорт' },
      ]}
    />
  )
}
