import { HubPage } from '../components/HubPage'

export function OrdersHubPage() {
  return (
    <HubPage
      title="Заказы"
      subtitle="Управление заказами"
      breadcrumbs={[{ label: 'Главная', to: '/' }, { label: 'Заказы' }]}
      sections={[
        {
          title: 'Типы заказов',
          icon: '📦',
          items: [
            { to: '/orders/inbound', label: 'Входящие заказы', description: 'Заказы от поставщиков', icon: '📥' },
            { to: '/orders/outbound', label: 'Исходящие заказы', description: 'Заказы клиентов', icon: '📤' },
            { to: '/orders/return', label: 'Возвратные заказы', description: 'Возвраты от клиентов', icon: '🔄' },
          ],
        },
      ]}
    />
  )
}
