import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { warehousesConfig } from '../features/topology-warehouses/config'

export function TopologyWarehousesPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={warehousesConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Топология', to: '/' },
        { label: 'Склады' },
      ]}
    />
  )
}
