import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-list/EntityListPage'
import { rolesConfig } from '../features/roles/config'

export function RolesPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={rolesConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Система', to: '/' },
        { label: 'Роли' },
      ]}
    />
  )
}
