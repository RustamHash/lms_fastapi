import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { keepersConfig } from '../features/keepers/config'

export function KeepersPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={keepersConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Справочники', to: '/' },
        { label: 'Хранители' },
      ]}
    />
  )
}
