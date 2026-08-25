import type { ListPageConfig } from '../entity-system/types'

type CarrierRow = {
  id: number
  name: string
  phone: string
  email: string
  is_active: boolean
  is_deleted: boolean
}

export const carriersConfig: ListPageConfig<CarrierRow> = {
  entityKey: 'carriers',
  title: 'Перевозчики',
  apiUrl: '/api/v1/carriers',
  listPath: '/carriers',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'name', label: 'Название', type: 'text' },
    { id: 'phone', label: 'Телефон', type: 'text' },
    { id: 'email', label: 'Email', type: 'text' },
    { id: 'is_active', label: 'Активен', type: 'bool' },
  ],
  filters: [
    { id: 'name', type: 'text', label: 'Название' },
    { id: 'phone', type: 'text', label: 'Телефон' },
  ],

  columnOverrides: {
    id: { href: (row) => `/carriers/${row.id}` },
  },
}