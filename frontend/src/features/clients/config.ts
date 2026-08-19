import type { ListPageConfig } from '../entity-list/types'

type ClientRow = {
  id: number
  depositor_id: number
  external_id: string
  name: string
  legal_name: string
  inn: string
  kpp: string
  is_edo: boolean
  is_deleted: boolean
  is_active: boolean
}

export const clientConfig = {
  list: {
    entityKey: 'clients',
    title: 'Клиенты',
    apiUrl: '/api/v1/parties/clients',
    columns: [
      { id: 'id', label: 'ID', type: 'number' },
      { id: 'external_id', label: 'Внешний код', type: 'text' },
      { id: 'name', label: 'Наименование', type: 'text' },
      { id: 'legal_name', label: 'Полное', type: 'text' },
      { id: 'inn', label: 'ИНН', type: 'text' },
      { id: 'kpp', label: 'КПП', type: 'text' },
      { id: 'is_edo', label: 'ЭДО', type: 'bool' },
      { id: 'is_active', label: 'Активен', type: 'bool' },
      { id: 'is_deleted', label: 'Удалён', type: 'bool' },
    ],
    filters: [
      { id: 'name', type: 'text', label: 'Наименование' },
      { id: 'inn', type: 'text', label: 'ИНН' },
    ],
    toolbar: {
      createHref: '/reference/clients/new',
    },
    columnOverrides: {
      name: { href: (row) => `/reference/clients/${row.id}` },
    },
  } as ListPageConfig<ClientRow>,
}
