import type { ListPageConfig } from '../entity-system/types'

type RowRow = {
  id: number
  zone_id: number
  name: string
  row_type: string
  is_active: boolean
}

export const rowsConfig: ListPageConfig<RowRow> = {
  entityKey: 'topology_rows',
  title: 'Ряды',
  apiUrl: '/api/v1/warehouse/topology/rows',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'zone_id', label: 'Зона ID', type: 'number' },
    { id: 'name', label: 'Название', type: 'text' },
    { id: 'row_type', label: 'Тип ряда', type: 'text' },
    { id: 'is_active', label: 'Активен', type: 'bool' },
  ],
  filters: [
    { id: 'name', type: 'text', label: 'Название' },
    { id: 'zone_id', type: 'text', label: 'Зона ID' },
  ],

  columnOverrides: {
    id: { href: (row) => `/reference/topology-rows/${row.id}` },
  },
}