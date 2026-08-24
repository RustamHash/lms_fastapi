import { useNavigate } from 'react-router-dom'
import { useAuth, hasPermission } from '../auth/AuthContext'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { tariffConfig } from '../features/tariffs/config'

export function TariffsPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const canCreate = hasPermission(user, 'tariffs', 'create')
  return (
    <EntityListPage
      config={tariffConfig.list}
      onBack={() => navigate('/references')}
      canCreate={canCreate}
      breadcrumbs={[{ label: 'Справочники', to: '/references' }, { label: 'Тарифы' }]}
    />
  )
}
