import type { ListPageConfig } from '../entity-system/types'

type DeliveryOrderRow = {
  id: number
  number: string
  contract_id: number
  document_id: number | null
  trade_point_id: number
  contact_person: string
  phone: string
  delivery_date: string | null
  time_from: string | null
  time_to: string | null
  status: string
  is_edo: boolean
  comment: string
}

export const deliveryOrdersConfig: ListPageConfig<DeliveryOrderRow> = {
  entityKey: 'delivery-orders',
  title: 'Заказы на доставку',
  apiUrl: '/api/v1/delivery/orders',
  listPath: '/delivery/orders',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'number', label: 'Номер', type: 'text' },
    { id: 'status', label: 'Статус', type: 'text' },
    { id: 'trade_point_id', label: 'ТТ ID', type: 'number' },
    { id: 'delivery_date', label: 'Дата доставки', type: 'date' },
    { id: 'contact_person', label: 'Контакт', type: 'text' },
    { id: 'phone', label: 'Телефон', type: 'text' },
  ],
  filters: [
    { id: 'number', type: 'text', label: 'Номер' },
    { id: 'status', type: 'text', label: 'Статус' },
  ],

  columnOverrides: {
    id: { href: (row) => `/delivery/orders/${row.id}` },
  },
}