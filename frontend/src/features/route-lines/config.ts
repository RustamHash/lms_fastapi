import type { ListPageConfig } from '../entity-system/types'

type RouteLineRow = {
  id: number
  route_id: number
  order_id: number
  sequence: number
  status: string
}

export const routeLinesConfig: ListPageConfig<RouteLineRow> = {
  entityKey: 'route_lines',
  title: 'Строки маршрутов',
  apiUrl: '/api/v1/route-lines',
  listPath: '/route-lines',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'route_id', label: 'Маршрут ID', type: 'number' },
    { id: 'order_id', label: 'Заказ ID', type: 'number' },
    { id: 'sequence', label: 'Порядок', type: 'number' },
    { id: 'status', label: 'Статус', type: 'text' },
  ],
  filters: [
    { id: 'route_id', type: 'text', label: 'Маршрут ID' },
    { id: 'status', type: 'text', label: 'Статус' },
  ],

  columnOverrides: {
    id: { href: (row) => `/route-lines/${row.id}` },
  },
}