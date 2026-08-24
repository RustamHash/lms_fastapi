import type { ListPageConfig } from '../entity-system/types'

type VirtualWarehouseRow = {
  id: number
  warehouse_id: number
  name: string
  is_active: boolean
}

export const virtualWarehousesConfig: ListPageConfig<VirtualWarehouseRow> = {
  entityKey: 'virtual_warehouses',
  title: 'Виртуальные склады',
  apiUrl: '/api/v1/warehouse/topology/virtual-warehouses',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'warehouse_id', label: 'Склад ID', type: 'number' },
    { id: 'name', label: 'Название', type: 'text' },
    { id: 'is_active', label: 'Активен', type: 'bool' },
  ],
  filters: [
    { id: 'name', type: 'text', label: 'Название' },
    { id: 'warehouse_id', type: 'text', label: 'Склад ID' },
  ],

  columnOverrides: {
    id: { href: (row) => `/reference/virtual-warehouses/${row.id}` },
  },
}