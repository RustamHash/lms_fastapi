import { GenericDetailPage } from '../components/GenericDetailPage'

export function VehicleDetailPage() {
  return (
    <GenericDetailPage
      title="Транспорт"
      apiUrl="/api/v1/delivery/vehicles"
      backHref="/reference/vehicles"
      backLabel="← К транспорту"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'number', label: 'Гос. номер', type: 'text' as const },
        { key: 'brand', label: 'Марка', type: 'text' as const },
        { key: 'model', label: 'Модель', type: 'text' as const },
        { key: 'capacity', label: 'Грузоподъёмность', type: 'number' as const },
        { key: 'volume', label: 'Объём', type: 'number' as const },
        { key: 'carrier_id', label: 'Перевозчик ID', type: 'number' as const },
      ]}
    />
  )
}
