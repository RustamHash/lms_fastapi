import type { ListPageConfig } from '../entity-system/types'

type LpnRow = {
  id: number
  number: string
  status: string
}

export const lpnsConfig: ListPageConfig<LpnRow> = {
  entityKey: 'lpns',
  title: 'LPN',
  apiUrl: '/api/v1/warehouse/lpns',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'number', label: 'Номер LPN', type: 'text' },
    { id: 'status', label: 'Статус', type: 'text' },
  ],
  filters: [
    { id: 'number', type: 'text', label: 'Номер LPN' },
    { id: 'status', type: 'text', label: 'Статус' },
  ],

  columnOverrides: {
    id: { href: (row) => `/reference/lpns/${row.id}` },
  },
}