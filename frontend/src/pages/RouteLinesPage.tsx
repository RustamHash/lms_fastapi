import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { routeLinesConfig } from '../features/route-lines/config'

export function RouteLinesPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={routeLinesConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Доставка', to: '/' },
        { label: 'Строки маршрутов' },
      ]}
    />
  )
}
