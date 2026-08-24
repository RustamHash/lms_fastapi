import type { ListPageConfig } from '../entity-system/types'

type IntegrationProfileRow = {
  id: number
  depositor_id: number
  name: string
  source_type: string
  config: Record<string, unknown>
}

export const integrationProfilesConfig: ListPageConfig<IntegrationProfileRow> = {
  entityKey: 'integration_profiles',
  title: 'Профили интеграций',
  apiUrl: '/api/v1/integrations/profiles',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'name', label: 'Название', type: 'text' },
    { id: 'source_type', label: 'Тип источника', type: 'text' },
    { id: 'depositor_id', label: 'Поклажедатель ID', type: 'number' },
  ],
  toolbar: {
    createHref: '/integrations/profiles/new',
  },
  filters: [
    { id: 'name', type: 'text', label: 'Название' },
    { id: 'source_type', type: 'text', label: 'Тип источника' },
  ],

  columnOverrides: {
    id: { href: (row) => `/reference/integration-profiles/${row.id}` },
  },
}