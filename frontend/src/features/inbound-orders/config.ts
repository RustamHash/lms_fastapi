import type { ListPageConfig } from '../entity-system/types'

type InboundOrderRow = {
  id: number
  depositor_id: number
  warehouse_id: number | null
  number: string
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
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'number', label: 'Номер', type: 'text' },
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
    id: { href: (row) => `/reference/inbound-orders/${row.id}` },
  },
}