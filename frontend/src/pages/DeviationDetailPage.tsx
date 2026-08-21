import { GenericDetailPage } from '../components/GenericDetailPage'

export function DeviationDetailPage() {
  return (
    <GenericDetailPage
      title="Отклонение"
      apiUrl="/api/v1/deviations"
      backHref="/deviations"
      backLabel="← К отклонениям"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'deviation_type', label: 'Тип', type: 'text' as const },
        { key: 'order_id', label: 'Заказ ID', type: 'number' as const },
        { key: 'route_line_id', label: 'Строка маршрута', type: 'number' as const },
        { key: 'quantity', label: 'Количество', type: 'number' as const },
        { key: 'reason', label: 'Причина', type: 'text' as const },
      ]}
    />
  )
}
