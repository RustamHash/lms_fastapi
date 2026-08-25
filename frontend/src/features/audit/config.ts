import type { ListPageConfig } from '../entity-system/types'

type AuditRow = {
  id: number
  user_id: number | null
  action: string
  entity_type: string
  entity_id: string | null
  changes: Record<string, unknown>
  ip_address: string
  user_agent: string
  created_at: string
  updated_at: string
}

export const auditConfig: ListPageConfig<AuditRow> = {
  entityKey: 'audit',
  title: 'Аудит',
  apiUrl: '/api/v1/audit',
  listPath: '/audit',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'user_id', label: 'Пользователь', type: 'number' },
    { id: 'action', label: 'Действие', type: 'text' },
    { id: 'entity_type', label: 'Тип объекта', type: 'text' },
    { id: 'entity_id', label: 'ID объекта', type: 'text' },
    { id: 'ip_address', label: 'IP адрес', type: 'text' },
    { id: 'created_at', label: 'Создан', type: 'date' },
  ],
  filters: [
    { id: 'action', type: 'text', label: 'Действие' },
    { id: 'entity_type', type: 'text', label: 'Тип объекта' },
    { id: 'user_id', type: 'text', label: 'Пользователь ID' },
  ],

  columnOverrides: {
    id: { href: (row) => `/audit/${row.id}` },
  },
}