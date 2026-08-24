import type { ListPageConfig } from '../entity-system/types'

type RoleRow = {
  id: number
  name: string
  code: string
  permissions: Record<string, unknown>
}

export const rolesConfig: ListPageConfig<RoleRow> = {
  entityKey: 'roles',
  title: 'Роли',
  apiUrl: '/api/v1/roles',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'name', label: 'Название', type: 'text' },
    { id: 'code', label: 'Код', type: 'text' },
  ],
  filters: [
    { id: 'name', type: 'text', label: 'Название' },
    { id: 'code', type: 'text', label: 'Код' },
  ],

  columnOverrides: {
    id: { href: (row) => `/reference/roles/${row.id}` },
  },
}