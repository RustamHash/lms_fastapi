import { GenericDetailPage } from '../components/GenericDetailPage'

export function TopologyLocationDetailPage() {
  return (
    <GenericDetailPage
      title="Ячейка"
      apiUrl="/api/v1/warehouse/topology/locations"
      backHref="/topology/locations"
      backLabel="← К ячейкам"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'row_id', label: 'Ряд ID', type: 'number' as const },
        { key: 'name', label: 'Название', type: 'text' as const },
        { key: 'location_type', label: 'Тип', type: 'text' as const },
        { key: 'capacity', label: 'Ёмкость', type: 'number' as const },
        { key: 'is_active', label: 'Активна', type: 'bool' as const },
      ]}
    />
  )
}
