import { GenericDetailPage } from '../components/GenericDetailPage'

export function DriverDetailPage() {
  return (
    <GenericDetailPage
      title="Водитель"
      apiUrl="/api/v1/delivery/drivers"
      backHref="/reference/drivers"
      backLabel="← К водителям"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'name', label: 'ФИО', type: 'text' as const },
        { key: 'phone', label: 'Телефон', type: 'text' as const },
        { key: 'carrier_id', label: 'Перевозчик ID', type: 'number' as const },
      ]}
    />
  )
}
