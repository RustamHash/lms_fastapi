import type { ListPageConfig } from '../entity-system/types'

type DeviationRow = {
  id: number
  order_id: number
  route_line_id: number | null
  deviation_type: string
  quantity: number
  reason: string
  created_at: string
}

export const deviationsConfig: ListPageConfig<DeviationRow> = {
  entityKey: 'deviations',
  title: 'Отклонения',
  apiUrl: '/api/v1/deviations',
  listPath: '/deviations',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'deviation_type', label: 'Тип', type: 'text' },
    { id: 'order_id', label: 'Заказ ID', type: 'number' },
    { id: 'route_line_id', label: 'Строка маршрута', type: 'number' },
    { id: 'quantity', label: 'Количество', type: 'number' },
    { id: 'reason', label: 'Причина', type: 'text' },
  ],
  filters: [
    { id: 'deviation_type', type: 'text', label: 'Тип' },
    { id: 'order_id', type: 'text', label: 'Заказ ID' },
  ],

  columnOverrides: {
    id: { href: (row) => `/deviations/${row.id}` },
  },
}