import type { ListPageConfig } from '../entity-system/types'

type LocationRow = {
  id: number
  row_id: number
  name: string
  location_type: string
  capacity: number | null
  is_active: boolean
}

export const locationsConfig: ListPageConfig<LocationRow> = {
  entityKey: 'topology_locations',
  title: 'Ячейки',
  apiUrl: '/api/v1/warehouse/topology/locations',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'row_id', label: 'Ряд ID', type: 'number' },
    { id: 'name', label: 'Название', type: 'text' },
    { id: 'location_type', label: 'Тип ячейки', type: 'text' },
    { id: 'capacity', label: 'Ёмкость', type: 'number' },
    { id: 'is_active', label: 'Активна', type: 'bool' },
  ],
  filters: [
    { id: 'name', type: 'text', label: 'Название' },
    { id: 'row_id', type: 'text', label: 'Ряд ID' },
  ],

  columnOverrides: {
    id: { href: (row) => `/reference/topology-locations/${row.id}` },
  },
}