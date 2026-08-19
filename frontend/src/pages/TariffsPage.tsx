import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { EntityListPage } from '../features/entity-list/EntityListPage'
import { tariffConfig } from '../features/tariffs/config'

export function TariffsPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const canCreate = user?.permissions?.all === true
  return (
    <EntityListPage
      config={tariffConfig.list}
      onBack={() => navigate('/references')}
      canCreate={canCreate}
      breadcrumbs={[{ label: 'Справочники', to: '/references' }, { label: 'Тарифы' }]}
    />
  )
}
