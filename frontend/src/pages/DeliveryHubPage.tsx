import { HubPage } from '../components/HubPage'

export function DeliveryHubPage() {
  return (
    <HubPage
      title="Доставка"
      subtitle="Управление доставкой"
      breadcrumbs={[{ label: 'Главная', to: '/' }, { label: 'Доставка' }]}
      sections={[
        {
          title: 'Доставка',
          icon: '🚚',
          items: [
            { to: '/delivery/orders', label: 'Заказы на доставку', description: 'Заказы клиентов', icon: '📦' },
            { to: '/route-lines', label: 'Строки маршрутов', description: 'Строки маршрутов', icon: '📋' },
            { to: '/deviations', label: 'Отклонения', description: 'Отклонения при доставке', icon: '⚠️' },
          ],
        },
      ]}
    />
  )
}
