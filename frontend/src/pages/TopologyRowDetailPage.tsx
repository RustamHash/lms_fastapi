import { GenericDetailPage } from '../components/GenericDetailPage'

export function TopologyRowDetailPage() {
  return (
    <GenericDetailPage
      title="Ряд"
      apiUrl="/api/v1/warehouse/topology/rows"
      backHref="/topology/rows"
      backLabel="← К рядам"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'zone_id', label: 'Зона ID', type: 'number' as const },
        { key: 'name', label: 'Название', type: 'text' as const },
        { key: 'row_type', label: 'Тип', type: 'text' as const },
        { key: 'is_active', label: 'Активен', type: 'bool' as const },
      ]}
    />
  )
}
