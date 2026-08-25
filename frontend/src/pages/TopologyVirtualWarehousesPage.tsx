import { useNavigate } from 'react-router-dom'
import { useAuth, hasPermission } from '../auth/AuthContext'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { virtualWarehousesConfig } from '../features/topology-virtual-warehouses/config'

export function TopologyVirtualWarehousesPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const canCreate = hasPermission(user, 'warehouse', 'create')
  return (
    <EntityListPage
      config={virtualWarehousesConfig}
      canCreate={canCreate}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Топология', to: '/topology' },
        { label: 'Виртуальные склады' },
      ]}
    />
  )
}
