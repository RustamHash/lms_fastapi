import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { locationsConfig } from '../features/topology-locations/config'

export function TopologyLocationsPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={locationsConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Топология', to: '/' },
        { label: 'Ячейки' },
      ]}
    />
  )
}
