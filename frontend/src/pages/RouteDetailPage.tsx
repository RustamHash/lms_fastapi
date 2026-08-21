import { GenericDetailPage } from '../components/GenericDetailPage'

export function RouteDetailPage() {
  return (
    <GenericDetailPage
      title="Маршрут"
      apiUrl="/api/v1/delivery/routes"
      backHref="/reference/routes"
      backLabel="← К маршрутам"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'number', label: 'Номер', type: 'text' as const },
        { key: 'date', label: 'Дата', type: 'date' as const },
        { key: 'status', label: 'Статус', type: 'text' as const },
        { key: 'driver_id', label: 'Водитель ID', type: 'number' as const },
        { key: 'vehicle_id', label: 'Транспорт ID', type: 'number' as const },
      ]}
    />
  )
}
