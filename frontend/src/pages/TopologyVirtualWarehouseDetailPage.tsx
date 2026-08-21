import { GenericDetailPage } from '../components/GenericDetailPage'

export function TopologyVirtualWarehouseDetailPage() {
  return (
    <GenericDetailPage
      title="Виртуальный склад"
      apiUrl="/api/v1/warehouse/topology/virtual-warehouses"
      backHref="/topology/virtual-warehouses"
      backLabel="← К виртуальным складам"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'warehouse_id', label: 'Склад ID', type: 'number' as const },
        { key: 'name', label: 'Название', type: 'text' as const },
        { key: 'is_active', label: 'Активен', type: 'bool' as const },
      ]}
    />
  )
}
