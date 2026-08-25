import type { ListPageConfig } from '../entity-system/types'

type StockRow = {
  id: number
  product_id: number
  location_id: number
  lpn_id: number
  batch_id: number
  quantity: string
  reserved_quantity: string
}

export const stockConfig: ListPageConfig<StockRow> = {
  entityKey: 'stock',
  title: 'Остатки на складе',
  apiUrl: '/api/v1/warehouse/stock',
  listPath: '/stock',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'product_id', label: 'Товар ID', type: 'number' },
    { id: 'location_id', label: 'Ячейка ID', type: 'number' },
    { id: 'lpn_id', label: 'LPN ID', type: 'number' },
    { id: 'batch_id', label: 'Партия ID', type: 'number' },
    { id: 'quantity', label: 'Количество', type: 'text' },
    { id: 'reserved_quantity', label: 'Зарезервировано', type: 'text' },
  ],
  filters: [
    { id: 'product_id', type: 'text', label: 'Товар ID' },
    { id: 'location_id', type: 'text', label: 'Ячейка ID' },
    { id: 'batch_id', type: 'text', label: 'Партия ID' },
  ],

  columnOverrides: {
    id: { href: (row) => `/stock/${row.id}` },
  },
}