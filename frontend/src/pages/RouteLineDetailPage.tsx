import { GenericDetailPage } from '../components/GenericDetailPage'

export function RouteLineDetailPage() {
  return (
    <GenericDetailPage
      title="Строка маршрута"
      apiUrl="/api/v1/route-lines"
      backHref="/route-lines"
      backLabel="← К строкам маршрутов"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'route_id', label: 'Маршрут ID', type: 'number' as const },
        { key: 'delivery_order_id', label: 'Заказ доставки ID', type: 'number' as const },
        { key: 'order', label: 'Порядок', type: 'number' as const },
        { key: 'status', label: 'Статус', type: 'text' as const },
      ]}
    />
  )
}
