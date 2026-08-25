import type { ListPageConfig } from '../entity-system/types'
import { getStatusLabel } from '../../lib/statusLabels'

type InboundOrderRow = {
  id: number
  depositor_id: number
  warehouse_id: number | null
  warehouse_name: string
  number: string
  order_number: string
  loc_code: string
  supplier_code: string
  order_date: string
  planned_date: string | null
  notes: string
  status: string
  pordrsp_exported: boolean
  recadv_exported: boolean
  has_shortage: boolean
}

export const inboundOrdersConfig: ListPageConfig<InboundOrderRow> = {
  entityKey: 'inbound_orders',
  title: 'Входящие заказы',
  apiUrl: '/api/v1/inbound-orders',
  listPath: '/orders/inbound',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'number', label: 'Номер заявки', type: 'text' },
    { id: 'order_number', label: 'Номер заказа', type: 'text' },
    { id: 'loc_code', label: 'Код склада', type: 'text' },
    { id: 'warehouse_name', label: 'Склад', type: 'text' },
    { id: 'supplier_code', label: 'Поставщик', type: 'text' },
    { id: 'order_date', label: 'Дата заказа', type: 'date' },
    { id: 'planned_date', label: 'Плановая дата', type: 'date' },
    { id: 'status', label: 'Статус', type: 'text' },
    { id: 'has_shortage', label: 'Недостача', type: 'bool' },
    { id: 'pordrsp_exported', label: 'PORDRSP', type: 'bool' },
    { id: 'recadv_exported', label: 'RECADV', type: 'bool' },
  ],
  filters: [
    { id: 'number', type: 'text', label: 'Номер' },
    { id: 'supplier_code', type: 'text', label: 'Поставщик' },
    { id: 'status', type: 'text', label: 'Статус' },
  ],

  columnOverrides: {
    id: { href: (row) => `/orders/inbound/${row.id}` },
    number: { href: (row) => `/orders/inbound/${row.id}` },
    status: { render: (row) => getStatusLabel(row.status) },
  },
}