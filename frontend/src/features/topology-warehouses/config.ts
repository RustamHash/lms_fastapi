import type { ListPageConfig } from '../entity-system/types'

type WarehouseRow = {
  id: number
  name: string
  address_id: number | null
  is_active: boolean
}

export const warehousesConfig: ListPageConfig<WarehouseRow> = {
  entityKey: 'warehouses',
  title: 'Склады',
  apiUrl: '/api/v1/warehouse/topology/warehouses',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'name', label: 'Название', type: 'text' },
    { id: 'address_id', label: 'Адрес ID', type: 'number' },
    { id: 'is_active', label: 'Активен', type: 'bool' },
  ],
  filters: [
    { id: 'name', type: 'text', label: 'Название' },
  ],

  columnOverrides: {
    id: { href: (row) => `/reference/warehouses/${row.id}` },
  },
}