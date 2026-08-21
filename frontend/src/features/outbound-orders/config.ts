import type { ListPageConfig } from '../entity-system/types'

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
  status_label: string
  is_edo: boolean
  warehouse_id: number
  declared_weight: string | null
  needs_delivery: boolean
  notes: string
  address_comment: string
  shipping_contact: string
  total_quantity: number
  total_lines: number
  depositor_name: string
  zone_name: string | null
  warehouse_name: string
  route_number: string | null
  driver_name: string | null
  driver_phone: string | null
}

export const outboundOrdersConfig: ListPageConfig<OutboundOrderRow> = {
  entityKey: 'outbound_orders',
  title: 'Исходящие заказы',
  apiUrl: '/api/v1/outbound-orders/list',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'number', label: 'Номер', type: 'text' },
    { id: 'customer_name', label: 'Клиент', type: 'text' },
    { id: 'delivery_address_name', label: 'Адрес доставки', type: 'text' },
    { id: 'order_date', label: 'Дата заказа', type: 'date' },
    { id: 'shipping_date', label: 'Дата отгрузки', type: 'date' },
    { id: 'status_label', label: 'Статус', type: 'text' },
    { id: 'depositor_name', label: 'Поклажедатель', type: 'text' },
    { id: 'warehouse_name', label: 'Склад', type: 'text' },
    { id: 'total_lines', label: 'Строк', type: 'number' },
    { id: 'total_quantity', label: 'Кол-во', type: 'number' },
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
  },
}
