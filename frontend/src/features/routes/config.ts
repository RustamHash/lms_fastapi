import type { ListPageConfig } from '../entity-system/types'

type RouteRow = {
  id: number
  number: string
  driver_id: number
  vehicle_id: number
  date: string
  status: string
}

export const routesConfig: ListPageConfig<RouteRow> = {
  entityKey: 'routes',
  title: 'Маршруты',
  apiUrl: '/api/v1/delivery/routes',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'number', label: 'Номер', type: 'text' },
    { id: 'date', label: 'Дата', type: 'date' },
    { id: 'status', label: 'Статус', type: 'text' },
    { id: 'driver_id', label: 'Водитель ID', type: 'number' },
    { id: 'vehicle_id', label: 'Транспорт ID', type: 'number' },
  ],
  filters: [
    { id: 'number', type: 'text', label: 'Номер' },
    { id: 'status', type: 'text', label: 'Статус' },
  ],

  columnOverrides: {
    id: { href: (row) => `/reference/routes/${row.id}` },
  },
}