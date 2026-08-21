import { GenericDetailPage } from '../components/GenericDetailPage'

export function ReturnOrderDetailPage() {
  return (
    <GenericDetailPage
      title="Возвратный заказ"
      apiUrl="/api/v1/return-orders"
      backHref="/orders/return"
      backLabel="← К возвратным заказам"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'customer_name', label: 'Клиент', type: 'text' as const },
        { key: 'return_date', label: 'Дата возврата', type: 'date' as const },
        { key: 'return_type', label: 'Тип возврата', type: 'text' as const },
        { key: 'status', label: 'Статус', type: 'text' as const },
        { key: 'outbound_order_id', label: 'Исходящий заказ ID', type: 'number' as const },
      ]}
    />
  )
}
