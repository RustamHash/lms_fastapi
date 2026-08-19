import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-list/EntityListPage'
import { deliveryZoneConfig } from '../features/delivery-zones/config'

export function DeliveryZonesPage() {
  const navigate = useNavigate()

  return (
    <EntityListPage
      config={deliveryZoneConfig.list}
      onBack={() => navigate('/references')}
      breadcrumbs={[
        { label: 'Справочники', to: '/references' },
        { label: 'Зоны доставки' },
      ]}
    />
  )
}
