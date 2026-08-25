import { useNavigate } from 'react-router-dom'
import { useAuth, hasPermission } from '../auth/AuthContext'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { warehousesConfig } from '../features/topology-warehouses/config'

export function TopologyWarehousesPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const canCreate = hasPermission(user, 'warehouse', 'create')
  return (
    <EntityListPage
      config={warehousesConfig}
      canCreate={canCreate}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Топология', to: '/topology' },
        { label: 'Склады' },
      ]}
    />
  )
}
