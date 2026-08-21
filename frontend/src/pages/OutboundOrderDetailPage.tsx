import { GenericDetailPage } from '../components/GenericDetailPage'

export function OutboundOrderDetailPage() {
  return (
    <GenericDetailPage
      title="Исходящий заказ"
      apiUrl="/api/v1/outbound-orders"
      backHref="/orders/outbound"
      backLabel="← К исходящим заказам"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'number', label: 'Номер', type: 'text' as const },
        { key: 'customer_name', label: 'Клиент', type: 'text' as const },
        { key: 'delivery_address_name', label: 'Адрес доставки', type: 'text' as const },
        { key: 'order_date', label: 'Дата заказа', type: 'date' as const },
        { key: 'shipping_date', label: 'Дата отгрузки', type: 'date' as const },
        { key: 'status', label: 'Статус', type: 'text' as const },
        { key: 'delivery_status', label: 'Статус доставки', type: 'text' as const },
        { key: 'needs_delivery', label: 'Доставка', type: 'bool' as const },
        { key: 'document_number', label: 'Документ', type: 'text' as const },
        { key: 'is_printed', label: 'Напечатан', type: 'bool' as const },
      ]}
    />
  )
}
