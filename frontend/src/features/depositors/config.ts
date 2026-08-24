import type { ListPageConfig } from '../entity-system/types'

type DepositorRow = {
  id: number
  code: string
  legal_entity_id: number
  legal_entity: {
    id: number
    name: string
    legal_name: string
    inn: string
    kpp: string
  } | null
  is_deleted: boolean
  is_active: boolean
}

export const depositorConfig = {
  list: {
    entityKey: 'depositors',
    title: 'Поклажедатели',
    apiUrl: '/api/v1/depositors',
    columns: [
      { id: 'id', label: 'ID', type: 'number' },
      { id: 'legal_entity.name', label: 'Юрлицо', type: 'text' },
      { id: 'code', label: 'Код', type: 'text' },
      { id: 'is_active', label: 'Активен', type: 'bool' },
      { id: 'is_deleted', label: 'Удалён', type: 'bool' },
    ],
    filters: [
      { id: 'legal_entity.name', type: 'text', label: 'Юрлицо' },
      { id: 'code', type: 'text', label: 'Код' },
    ],
    toolbar: {
      createHref: '/reference/depositors/new',
    },
    columnOverrides: {
      id: { href: (row) => `/reference/depositors/${row.id}` },
    },
  } as ListPageConfig<DepositorRow>,
}