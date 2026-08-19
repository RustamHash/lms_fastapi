import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { EntityListPage } from '../features/entity-list/EntityListPage'
import { clientConfig } from '../features/clients/config'

export function ClientsPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const canCreate = user?.permissions?.all === true
  return (
    <EntityListPage
      config={clientConfig.list}
      onBack={() => navigate('/references')}
      canCreate={canCreate}
      breadcrumbs={[{ label: 'Справочники', to: '/references' }, { label: 'Клиенты' }]}
    />
  )
}
