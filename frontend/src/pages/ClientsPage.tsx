import { useNavigate } from 'react-router-dom'
import { useAuth, hasPermission } from '../auth/AuthContext'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { clientConfig } from '../features/clients/config'

export function ClientsPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const canCreate = hasPermission(user, 'clients', 'create')
  return (
    <EntityListPage
      config={clientConfig.list}
      onBack={() => navigate('/references')}
      canCreate={canCreate}
      breadcrumbs={[{ label: 'Справочники', to: '/references' }, { label: 'Клиенты' }]}
    />
  )
}
