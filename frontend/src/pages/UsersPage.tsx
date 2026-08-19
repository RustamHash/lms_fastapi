import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-list/EntityListPage'
import { usersConfig } from '../features/users/config'

export function UsersPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={usersConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Система', to: '/' },
        { label: 'Пользователи' },
      ]}
    />
  )
}
