import type { ListPageConfig } from '../entity-system/types'
import { getStatusLabel } from '../../lib/statusLabels'

type OutboundOrderRow = {
  id: number
  number: string
  customer_code: string
  customer_name: string
  document_number: string
  delivery_address_name: string
  order_date: string
  shipping_date: string | null
  status: string
  warehouse_id: number | null
  declared_weight: string | null
  needs_delivery: boolean
  notes: string
}

export const outboundOrdersConfig: ListPageConfig<OutboundOrderRow> = {
  entityKey: 'outbound_orders',
  title: 'Исходящие заказы',
  apiUrl: '/api/v1/outbound-orders',
  listPath: '/orders/outbound',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'number', label: 'Номер', type: 'text' },
    { id: 'customer_name', label: 'Клиент', type: 'text' },
    { id: 'delivery_address_name', label: 'Адрес доставки', type: 'text' },
    { id: 'order_date', label: 'Дата заказа', type: 'date' },
    { id: 'shipping_date', label: 'Дата отгрузки', type: 'date' },
    { id: 'status', label: 'Статус', type: 'text' },
    { id: 'needs_delivery', label: 'Доставка', type: 'bool' },
    { id: 'document_number', label: 'Документ', type: 'text' },
  ],
  filters: [
    { id: 'number', type: 'text', label: 'Номер' },
    { id: 'customer_name', type: 'text', label: 'Клиент' },
    { id: 'delivery_address_name', type: 'text', label: 'Адрес доставки' },
    { id: 'status', type: 'text', label: 'Статус' },
    { id: 'delivery_status', type: 'text', label: 'Статус доставки' },
  ],

  columnOverrides: {
    id: { href: (row) => `/orders/outbound/${row.id}` },
    number: { href: (row) => `/orders/outbound/${row.id}` },
    status: { render: (row) => getStatusLabel(row.status) },
  },
}