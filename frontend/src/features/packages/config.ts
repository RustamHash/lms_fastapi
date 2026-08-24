import type { ListPageConfig } from '../entity-system/types'

type PackageRow = {
  id: number
  name: string
  package_type: string
  weight: string | null
  volume: string | null
  is_active: boolean
}

export const packagesConfig: ListPageConfig<PackageRow> = {
  entityKey: 'packages',
  title: 'Упаковки',
  apiUrl: '/api/v1/warehouse/packages',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'name', label: 'Название', type: 'text' },
    { id: 'package_type', label: 'Тип', type: 'text' },
    { id: 'weight', label: 'Вес', type: 'text' },
    { id: 'volume', label: 'Объём', type: 'text' },
    { id: 'is_active', label: 'Активна', type: 'bool' },
  ],
  filters: [
    { id: 'name', type: 'text', label: 'Название' },
  ],

  columnOverrides: {
    id: { href: (row) => `/reference/packages/${row.id}` },
  },
}