import { useNavigate } from 'react-router-dom'
import { useAuth, hasPermission } from '../auth/AuthContext'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { legalEntityConfig } from '../features/legal-entities/config'

export function LegalEntitiesPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const canCreate = hasPermission(user, 'legal_entities', 'create')
  return (
    <EntityListPage
      config={legalEntityConfig.list}
      onBack={() => navigate('/references')}
      canCreate={canCreate}
      breadcrumbs={[{ label: 'Справочники', to: '/references' }, { label: 'Юрлица' }]}
    />
  )
}
