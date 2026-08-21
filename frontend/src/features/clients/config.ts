import type { ListPageConfig } from '../entity-system/types'

type ClientRow = {
  id: number
  depositor_id: number
  code: string
  name: string
  legal_name: string
  inn: string
  kpp: string
  legal_address_id: number | null
  delivery_address_id: number
  is_edo: boolean
}

export const clientConfig = {
  list: {
    entityKey: 'clients',
    title: 'Клиенты',
    apiUrl: '/api/v1/parties/clients',
    columns: [
      { id: 'id', label: 'ID', type: 'number' },
      { id: 'code', label: 'Код клиента', type: 'text' },
      { id: 'name', label: 'Наименование', type: 'text' },
      { id: 'legal_name', label: 'Полное', type: 'text' },
      { id: 'inn', label: 'ИНН', type: 'text' },
      { id: 'kpp', label: 'КПП', type: 'text' },
      { id: 'depositor_id', label: 'Поклажедатель', type: 'number' },
      { id: 'legal_address_id', label: 'Юр. адрес', type: 'number' },
      { id: 'delivery_address_id', label: 'Адрес доставки', type: 'number' },
      { id: 'is_edo', label: 'ЭДО', type: 'bool' },
    ],
    filters: [
      { id: 'code', type: 'text', label: 'Код клиента' },
      { id: 'name', type: 'text', label: 'Наименование' },
      { id: 'inn', type: 'text', label: 'ИНН' },
    ],
    toolbar: {
      createHref: '/reference/clients/new',
    },
    columnOverrides: {
      name: { href: (row) => `/reference/clients/${row.id}` },
      code: { href: (row) => `/reference/clients/${row.id}` },
    },
  } as ListPageConfig<ClientRow>,
}
