import type { ListPageConfig } from '../entity-system/types'

type ProductGroupRow = {
  id: number
  name: string
  parent_id: number | null
  is_active: boolean
}

export const productGroupsConfig: ListPageConfig<ProductGroupRow> = {
  entityKey: 'product_groups',
  title: 'Группы товаров',
  apiUrl: '/api/v1/warehouse/product-groups',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'name', label: 'Название', type: 'text' },
    { id: 'parent_id', label: 'Родительская группа', type: 'number' },
    { id: 'is_active', label: 'Активна', type: 'bool' },
  ],
  filters: [
    { id: 'name', type: 'text', label: 'Название' },
  ],
  columnOverrides: {
    name: { href: (row) => `/reference/product-groups/${row.id}` },
  },
}
