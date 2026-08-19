import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { EntityListPage } from '../features/entity-list/EntityListPage'
import { depositorConfig } from '../features/depositors/config'

export function DepositorsPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const canCreate = user?.permissions?.all === true
  return (
    <EntityListPage
      config={depositorConfig.list}
      onBack={() => navigate('/references')}
      canCreate={canCreate}
      breadcrumbs={[{ label: 'Справочники', to: '/references' }, { label: 'Поклажедатели' }]}
    />
  )
}
