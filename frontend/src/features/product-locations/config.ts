import type { ListPageConfig } from '../entity-system/types'

type ProductLocationRow = {
  id: number
  product_id: number
  location_id: number
  quantity: string
  is_active: boolean
}

export const productLocationsConfig: ListPageConfig<ProductLocationRow> = {
  entityKey: 'product_locations',
  title: 'Товар-ячейка',
  apiUrl: '/api/v1/warehouse/product-locations',
  listPath: '/reference/product-locations',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'product_id', label: 'Товар ID', type: 'number' },
    { id: 'location_id', label: 'Ячейка ID', type: 'number' },
    { id: 'quantity', label: 'Количество', type: 'text' },
    { id: 'is_active', label: 'Активна', type: 'bool' },
  ],
  filters: [
    { id: 'product_id', type: 'text', label: 'Товар ID' },
    { id: 'location_id', type: 'text', label: 'Ячейка ID' },
  ],

  columnOverrides: {
    id: { href: (row) => `/reference/product-locations/${row.id}` },
  },
}