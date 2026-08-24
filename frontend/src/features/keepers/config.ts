import type { ListPageConfig } from '../entity-system/types'

type KeeperRow = {
  id: number
  name: string
  phone: string
  email: string
  is_active: boolean
  is_deleted: boolean
}

export const keepersConfig: ListPageConfig<KeeperRow> = {
  entityKey: 'keepers',
  title: 'Хранители',
  apiUrl: '/api/v1/keepers',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'name', label: 'Название', type: 'text' },
    { id: 'phone', label: 'Телефон', type: 'text' },
    { id: 'email', label: 'Email', type: 'text' },
    { id: 'is_active', label: 'Активен', type: 'bool' },
  ],
  filters: [
    { id: 'name', type: 'text', label: 'Название' },
  ],

  columnOverrides: {
    id: { href: (row) => `/reference/keepers/${row.id}` },
  },
}