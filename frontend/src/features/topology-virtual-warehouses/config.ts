import type { ListPageConfig } from '../entity-system/types'

type VirtualWarehouseRow = {
  id: number
  warehouse_id: number
  depositor_id: number
  code: string
  name: string
  is_active: boolean
}

export const virtualWarehousesConfig: ListPageConfig<VirtualWarehouseRow> = {
  entityKey: 'virtual_warehouses',
  title: 'Виртуальные склады',
  apiUrl: '/api/v1/warehouse/topology/virtual-warehouses',
  listPath: '/topology/virtual-warehouses',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'warehouse_id', label: 'Склад ID', type: 'number' },
    { id: 'depositor_id', label: 'Поклажедатель', type: 'number' },
    { id: 'code', label: 'Код', type: 'text' },
    { id: 'name', label: 'Название', type: 'text' },
    { id: 'is_active', label: 'Активен', type: 'bool' },
  ],
  filters: [
    { id: 'name', type: 'text', label: 'Название' },
    { id: 'code', type: 'text', label: 'Код' },
    { id: 'warehouse_id', type: 'text', label: 'Склад ID' },
  ],
  toolbar: {
    createHref: '/topology/virtual-warehouses/new',
  },
  columnOverrides: {
    id: { href: (row) => `/topology/virtual-warehouses/${row.id}` },
  },
}