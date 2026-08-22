import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { packagesConfig } from '../features/packages/config'

export function PackagesPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={packagesConfig}
      onBack={() => navigate('/references')}
      breadcrumbs={[
        { label: 'Справочники', to: '/references' },
        { label: 'Упаковки' },
      ]}
    />
  )
}
