import type { ListPageConfig } from '../entity-list/types'

type IntegrationProfileRow = {
  id: number
  depositor_id: number
  name: string
  source_type: string
  config: Record<string, unknown>
}

export const integrationProfilesConfig: ListPageConfig<IntegrationProfileRow> = {
  entityKey: 'integration-profiles',
  title: 'Профили интеграций',
  apiUrl: '/api/v1/integrations/profiles',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'name', label: 'Название', type: 'text' },
    { id: 'source_type', label: 'Тип источника', type: 'text' },
    { id: 'depositor_id', label: 'Поклажедатель ID', type: 'number' },
  ],
  filters: [
    { id: 'name', type: 'text', label: 'Название' },
    { id: 'source_type', type: 'text', label: 'Тип источника' },
  ],
}
