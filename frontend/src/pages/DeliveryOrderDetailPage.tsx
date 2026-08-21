import { GenericDetailPage } from '../components/GenericDetailPage'

export function DeliveryOrderDetailPage() {
  return (
    <GenericDetailPage
      title="Заказ доставки"
      apiUrl="/api/v1/delivery/orders"
      backHref="/delivery/orders"
      backLabel="← К заказам доставки"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'number', label: 'Номер', type: 'text' as const },
        { key: 'contract_id', label: 'Договор ID', type: 'number' as const },
        { key: 'trade_point_id', label: 'ТТ ID', type: 'number' as const },
        { key: 'contact_person', label: 'Контакт', type: 'text' as const },
        { key: 'phone', label: 'Телефон', type: 'text' as const },
        { key: 'delivery_date', label: 'Дата доставки', type: 'date' as const },
        { key: 'status', label: 'Статус', type: 'text' as const },
        { key: 'is_edo', label: 'ЭДО', type: 'bool' as const },
      ]}
    />
  )
}
