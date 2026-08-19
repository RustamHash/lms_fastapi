import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { EntityListPage } from '../features/entity-list/EntityListPage'
import { contractConfig } from '../features/contracts/config'

export function ContractsPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const canCreate = user?.permissions?.all === true
  return (
    <EntityListPage
      config={contractConfig.list}
      onBack={() => navigate('/references')}
      canCreate={canCreate}
      breadcrumbs={[{ label: 'Справочники', to: '/references' }, { label: 'Договоры' }]}
    />
  )
}
