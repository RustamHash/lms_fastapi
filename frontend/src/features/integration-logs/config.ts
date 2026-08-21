import type { ListPageConfig } from '../entity-system/types'

type IntegrationLogRow = {
  id: number
  profile_id: number
  status: string
  total_rows: number
  success_rows: number
  error_rows: number
  file_id: number | null
}

export const integrationLogsConfig: ListPageConfig<IntegrationLogRow> = {
  entityKey: 'integration-logs',
  title: 'Логи интеграций',
  apiUrl: '/api/v1/integrations/logs',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'profile_id', label: 'Профиль ID', type: 'number' },
    { id: 'status', label: 'Статус', type: 'text' },
    { id: 'total_rows', label: 'Всего строк', type: 'number' },
    { id: 'success_rows', label: 'Успешно', type: 'number' },
    { id: 'error_rows', label: 'С ошибками', type: 'number' },
  ],
  filters: [
    { id: 'profile_id', type: 'text', label: 'Профиль ID' },
    { id: 'status', type: 'text', label: 'Статус' },
  ],
}
