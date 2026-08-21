import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { virtualWarehousesConfig } from '../features/topology-virtual-warehouses/config'

export function TopologyVirtualWarehousesPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={virtualWarehousesConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Топология', to: '/' },
        { label: 'Виртуальные склады' },
      ]}
    />
  )
}
