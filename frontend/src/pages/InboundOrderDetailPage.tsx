import { GenericDetailPage } from '../components/GenericDetailPage'

export function InboundOrderDetailPage() {
  return (
    <GenericDetailPage
      title="Входящий заказ"
      apiUrl="/api/v1/inbound-orders"
      backHref="/orders/inbound"
      backLabel="← К входящим заказам"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'number', label: 'Номер', type: 'text' as const },
        { key: 'supplier_code', label: 'Поставщик', type: 'text' as const },
        { key: 'order_date', label: 'Дата заказа', type: 'date' as const },
        { key: 'planned_date', label: 'Плановая дата', type: 'date' as const },
        { key: 'status', label: 'Статус', type: 'text' as const },
        { key: 'has_shortage', label: 'Недостача', type: 'bool' as const },
      ]}
    />
  )
}
