import type { ListPageConfig } from '../entity-system/types'

type OutboundOrderRow = {
  id: number
  depositor_id: number
  warehouse_id: number | null
  number: string
  customer_code: string
  customer_name: string
  delivery_address_name: string
  order_date: string
  shipping_date: string | null
  needs_delivery: boolean
  delivery_only: boolean
  places_count: number | null
  declared_weight: string | null
  delivery_contact: string
  notes: string
  status: string
  ordrsp_exported: boolean
  desadv_exported: boolean
  zone_id: number | null
  document_number: string
  is_printed: boolean
  delivery_status: string | null
}

export const outboundOrdersConfig: ListPageConfig<OutboundOrderRow> = {
  entityKey: 'outbound_orders',
  title: 'Исходящие заказы',
  apiUrl: '/api/v1/outbound-orders',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'number', label: 'Номер', type: 'text' },
    { id: 'customer_name', label: 'Клиент', type: 'text' },
    { id: 'delivery_address_name', label: 'Адрес доставки', type: 'text' },
    { id: 'order_date', label: 'Дата заказа', type: 'date' },
    { id: 'shipping_date', label: 'Дата отгрузки', type: 'date' },
    { id: 'status', label: 'Статус', type: 'text' },
    { id: 'delivery_status', label: 'Статус доставки', type: 'text' },
    { id: 'needs_delivery', label: 'Доставка', type: 'bool' },
    { id: 'document_number', label: 'Документ', type: 'text' },
    { id: 'is_printed', label: 'Напечатан', type: 'bool' },
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
  },
}
