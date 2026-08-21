import { GenericDetailPage } from '../components/GenericDetailPage'

export function TopologyZoneDetailPage() {
  return (
    <GenericDetailPage
      title="Зона склада"
      apiUrl="/api/v1/warehouse/topology/zones"
      backHref="/topology/zones"
      backLabel="← К зонам"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'warehouse_id', label: 'Склад ID', type: 'number' as const },
        { key: 'name', label: 'Название', type: 'text' as const },
        { key: 'zone_type', label: 'Тип', type: 'text' as const },
        { key: 'is_active', label: 'Активна', type: 'bool' as const },
      ]}
    />
  )
}
