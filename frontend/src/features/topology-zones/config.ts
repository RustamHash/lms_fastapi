import type { ListPageConfig } from '../entity-system/types'

type ZoneRow = {
  id: number
  warehouse_id: number
  name: string
  zone_type: string
  is_active: boolean
}

export const zonesConfig: ListPageConfig<ZoneRow> = {
  entityKey: 'topology_zones',
  title: 'Зоны склада',
  apiUrl: '/api/v1/warehouse/topology/zones',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'warehouse_id', label: 'Склад ID', type: 'number' },
    { id: 'name', label: 'Название', type: 'text' },
    { id: 'zone_type', label: 'Тип зоны', type: 'text' },
    { id: 'is_active', label: 'Активна', type: 'bool' },
  ],
  filters: [
    { id: 'name', type: 'text', label: 'Название' },
    { id: 'zone_type', type: 'text', label: 'Тип зоны' },
  ],
  columnOverrides: {
    id: { href: (row) => `/topology/zones/${row.id}` },
  },
}
