import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-list/EntityListPage'
import { driversConfig } from '../features/drivers/config'

export function DriversPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={driversConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Доставка', to: '/' },
        { label: 'Водители' },
      ]}
    />
  )
}
