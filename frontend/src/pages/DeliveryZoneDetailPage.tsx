import { GenericDetailPage } from '../components/GenericDetailPage'

export function DeliveryZoneDetailPage() {
  return (
    <GenericDetailPage
      title="Зона доставки"
      apiUrl="/api/v1/delivery-zones"
      backHref="/reference/delivery-zones"
      backLabel="← К зонам доставки"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'name', label: 'Название', type: 'text' as const },
        { key: 'is_active', label: 'Активна', type: 'bool' as const },
      ]}
    />
  )
}
