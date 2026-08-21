import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { carriersConfig } from '../features/carriers/config'

export function CarriersPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={carriersConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Справочники', to: '/' },
        { label: 'Перевозчики' },
      ]}
    />
  )
}
