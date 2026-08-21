import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { inboundOrdersConfig } from '../features/inbound-orders/config'

export function InboundOrdersPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={inboundOrdersConfig}
      onBack={() => navigate('/orders')}
      breadcrumbs={[
        { label: 'Главная', to: '/' },
        { label: 'Заказы', to: '/orders' },
        { label: 'Входящие' },
      ]}
    />
  )
}
