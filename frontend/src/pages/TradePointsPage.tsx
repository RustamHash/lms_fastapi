import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { tradePointConfig } from '../features/trade-points/config'

export function TradePointsPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const canCreate = user?.permissions?.all === true
  return (
    <EntityListPage
      config={tradePointConfig.list}
      onBack={() => navigate('/references')}
      canCreate={canCreate}
      breadcrumbs={[{ label: 'Справочники', to: '/references' }, { label: 'Торговые точки' }]}
    />
  )
}
