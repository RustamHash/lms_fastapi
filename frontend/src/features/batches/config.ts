import type { ListPageConfig } from '../entity-system/types'

type BatchRow = {
  id: number
  product_id: number
  batch_number: string
  production_date: string | null
  expiration_date: string | null
}

export const batchesConfig: ListPageConfig<BatchRow> = {
  entityKey: 'batches',
  title: 'Партии',
  apiUrl: '/api/v1/warehouse/batches',
  listPath: '/reference/batches',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'batch_number', label: 'Номер партии', type: 'text' },
    { id: 'product_id', label: 'Товар ID', type: 'number' },
    { id: 'production_date', label: 'Дата производства', type: 'date' },
    { id: 'expiration_date', label: 'Срок годности', type: 'date' },
  ],
  filters: [
    { id: 'batch_number', type: 'text', label: 'Номер партии' },
    { id: 'product_id', type: 'text', label: 'Товар ID' },
  ],

  columnOverrides: {
    id: { href: (row) => `/reference/batches/${row.id}` },
  },
}