import type { ListPageConfig } from '../entity-list/types'

type DepositorRow = {
  id: number
  code: string
  legal_entity_id: number
  legal_entity_name: string
  is_deleted: boolean
  is_active: boolean
}

export const depositorConfig = {
  list: {
    entityKey: 'depositors',
    title: 'Поклажедатели',
    apiUrl: '/api/v1/parties/depositors',
    columns: [
      { id: 'id', label: 'ID', type: 'number' },
      { id: 'legal_entity_name', label: 'Юрлицо', type: 'text' },
      { id: 'code', label: 'Код', type: 'text' },
      { id: 'is_active', label: 'Активен', type: 'bool' },
      { id: 'is_deleted', label: 'Удалён', type: 'bool' },
    ],
    filters: [
      { id: 'legal_entity_name', type: 'text', label: 'Юрлицо' },
      { id: 'code', type: 'text', label: 'Код' },
    ],
    columnOverrides: {
      legal_entity_name: { href: (row) => `/reference/depositors/${row.id}` },
    },
    toolbar: {
      createHref: '/reference/depositors/new',
    },
  } as ListPageConfig<DepositorRow>,
}
