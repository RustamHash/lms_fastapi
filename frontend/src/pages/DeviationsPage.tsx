import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { deviationsConfig } from '../features/deviations/config'

export function DeviationsPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={deviationsConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Доставка', to: '/' },
        { label: 'Отклонения' },
      ]}
    />
  )
}
