import type { ListPageConfig } from '../entity-system/types'

type IntegrationLogRow = {
  id: number
  profile_id: number | null
  status: string
  document_type: string | null
  total_rows: number
  success_rows: number
  error_rows: number
  created_at: string
  file_id: number | null
}

export const integrationLogsConfig: ListPageConfig<IntegrationLogRow> = {
  entityKey: 'integration_logs',
  title: 'Логи интеграций',
  apiUrl: '/api/v1/integrations/logs',
  listPath: '/integrations/logs',
  staleTime: 15 * 1000,
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'status', label: 'Статус', type: 'text' },
    { id: 'document_type', label: 'Тип', type: 'text' },
    { id: 'total_rows', label: 'Всего', type: 'number' },
    { id: 'success_rows', label: 'Успешно', type: 'number' },
    { id: 'error_rows', label: 'Ошибок', type: 'number' },
    { id: 'created_at', label: 'Создан', type: 'datetime' },
  ],
  filters: [
    { id: 'status', type: 'text', label: 'Статус' },
    { id: 'document_type', type: 'text', label: 'Тип' },
  ],
  defaultSort: { column: 'id', direction: 'desc' },
  toolbar: {
    disableCreate: true,
  },
  columnOverrides: {
    id: { href: (row) => `/integrations/logs/${row.id}` },
  },
}
