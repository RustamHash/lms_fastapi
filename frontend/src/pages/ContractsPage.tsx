import { useNavigate } from 'react-router-dom'
import { useAuth, hasPermission } from '../auth/AuthContext'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { contractConfig } from '../features/contracts/config'

export function ContractsPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const canCreate = hasPermission(user, 'contracts', 'create')
  return (
    <EntityListPage
      config={contractConfig.list}
      onBack={() => navigate('/references')}
      canCreate={canCreate}
      breadcrumbs={[{ label: 'Справочники', to: '/references' }, { label: 'Договоры' }]}
    />
  )
}
