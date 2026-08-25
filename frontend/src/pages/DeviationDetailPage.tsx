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
        { key: 'delivery_order_id', label: 'Заказ доставки ID', type: 'number' as const },
        { key: 'quantity', label: 'Количество', type: 'number' as const },
        { key: 'description', label: 'Описание', type: 'text' as const },
      ]}
    />
  )
}
