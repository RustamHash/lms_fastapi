import { GenericDetailPage } from '../components/GenericDetailPage'

export function TopologyWarehouseDetailPage() {
  return (
    <GenericDetailPage
      title="Склад"
      apiUrl="/api/v1/warehouse/topology/warehouses"
      backHref="/topology/warehouses"
      backLabel="← К складам"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'name', label: 'Название', type: 'text' as const },
        { key: 'address_id', label: 'Адрес ID', type: 'number' as const },
        { key: 'is_active', label: 'Активен', type: 'bool' as const },
      ]}
    />
  )
}
