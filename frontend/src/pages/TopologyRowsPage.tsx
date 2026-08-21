import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { rowsConfig } from '../features/topology-rows/config'

export function TopologyRowsPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={rowsConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Топология', to: '/' },
        { label: 'Ряды' },
      ]}
    />
  )
}
