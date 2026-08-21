import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { returnOrdersConfig } from '../features/return-orders/config'

export function ReturnOrdersPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={returnOrdersConfig}
      onBack={() => navigate('/orders')}
      breadcrumbs={[
        { label: 'Главная', to: '/' },
        { label: 'Заказы', to: '/orders' },
        { label: 'Возвратные' },
      ]}
    />
  )
}
