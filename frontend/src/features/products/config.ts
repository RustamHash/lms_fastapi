import type { ListPageConfig } from '../entity-system/types'

type ProductRow = {
  id: number
  depositor_id: number
  external_id: string
  name: string
  sku: string
  legal_name: string
  weight: string
  volume: string
  price: string | null
  shelf_life_days: number | null
  min_shelf_life_days: number | null
  is_marked: boolean
  is_serial_tracked: boolean
  is_batch_tracked: boolean
  is_expiration_tracked: boolean
  temperature_requirements: string
}

export const productsConfig: ListPageConfig<ProductRow> = {
  entityKey: 'products',
  title: 'Товары',
  apiUrl: '/api/v1/warehouse/products',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'name', label: 'Название', type: 'text' },
    { id: 'sku', label: 'SKU', type: 'text' },
    { id: 'external_id', label: 'Внешний ID', type: 'text' },
    { id: 'depositor_id', label: 'Поклажедатель', type: 'number' },
    { id: 'weight', label: 'Вес', type: 'text' },
    { id: 'volume', label: 'Объём', type: 'text' },
    { id: 'price', label: 'Цена', type: 'text' },
    { id: 'is_marked', label: 'Маркировка', type: 'bool' },
    { id: 'is_batch_tracked', label: 'Партионный учёт', type: 'bool' },
  ],
  filters: [
    { id: 'name', type: 'text', label: 'Название' },
    { id: 'sku', type: 'text', label: 'SKU' },
    { id: 'depositor_id', type: 'text', label: 'Поклажедатель ID' },
  ],

  columnOverrides: {
    id: { href: (row) => `/reference/products/${row.id}` },
  },
}