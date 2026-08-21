import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { deliveryOrdersConfig } from '../features/delivery-orders/config'

export function DeliveryOrdersPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={deliveryOrdersConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Главная', to: '/' },
        { label: 'Заказы' },
      ]}
    />
  )
}
