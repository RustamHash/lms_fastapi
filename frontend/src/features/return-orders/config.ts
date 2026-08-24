import type { ListPageConfig } from '../entity-system/types'

type ReturnOrderRow = {
  id: number
  outbound_order_id: number
  inbound_order_id: number | null
  depositor_id: number
  warehouse_id: number | null
  customer_code: string
  customer_name: string
  return_date: string
  return_type: string
  status: string
  notes: string
}

export const returnOrdersConfig: ListPageConfig<ReturnOrderRow> = {
  entityKey: 'return_orders',
  title: 'Возвратные заказы',
  apiUrl: '/api/v1/return-orders',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'customer_name', label: 'Клиент', type: 'text' },
    { id: 'return_date', label: 'Дата возврата', type: 'date' },
    { id: 'return_type', label: 'Тип возврата', type: 'text' },
    { id: 'status', label: 'Статус', type: 'text' },
    { id: 'outbound_order_id', label: 'Исходящий заказ', type: 'number' },
  ],
  filters: [
    { id: 'customer_name', type: 'text', label: 'Клиент' },
    { id: 'return_type', type: 'text', label: 'Тип возврата' },
    { id: 'status', type: 'text', label: 'Статус' },
  ],

  columnOverrides: {
    id: { href: (row) => `/reference/return-orders/${row.id}` },
  },
}