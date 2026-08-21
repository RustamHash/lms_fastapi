import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { outboundOrdersConfig } from '../features/outbound-orders/config'

export function OutboundOrdersPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={outboundOrdersConfig}
      onBack={() => navigate('/orders')}
      breadcrumbs={[
        { label: 'Главная', to: '/' },
        { label: 'Заказы', to: '/orders' },
        { label: 'Исходящие' },
      ]}
    />
  )
}
