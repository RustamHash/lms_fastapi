import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { zonesConfig } from '../features/topology-zones/config'

export function TopologyZonesPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={zonesConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Топология', to: '/' },
        { label: 'Зоны' },
      ]}
    />
  )
}
