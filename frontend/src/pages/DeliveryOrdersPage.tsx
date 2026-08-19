import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-list/EntityListPage'
import { deliveryOrdersConfig } from '../features/delivery-orders/config'

export function DeliveryOrdersPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={deliveryOrdersConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Доставка', to: '/' },
        { label: 'Заказы' },
      ]}
    />
  )
}
