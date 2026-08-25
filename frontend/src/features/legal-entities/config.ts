import type { ListPageConfig } from '../entity-system/types'

type LegalEntityRow = {
  id: number
  name: string
  legal_name: string
  inn: string
  kpp: string
  ogrn: string
  legal_address_id: number | null
  actual_address_id: number | null
  phone: string
  email: string
  edo_uuid: string | null
}

export const legalEntityConfig = {
  list: {
    entityKey: 'legal_entities',
    title: 'Юридические лица',
    apiUrl: '/api/v1/legal-entities',
    listPath: '/reference/legal-entities',
    columns: [
      { id: 'id', label: 'ID', type: 'number' },
      { id: 'name', label: 'Наименование', type: 'text' },
      { id: 'legal_name', label: 'Полное', type: 'text' },
      { id: 'inn', label: 'ИНН', type: 'text' },
      { id: 'kpp', label: 'КПП', type: 'text' },
      { id: 'ogrn', label: 'ОГРН', type: 'text' },
      { id: 'phone', label: 'Телефон', type: 'text' },
      { id: 'email', label: 'Email', type: 'text' },
      { id: 'is_active', label: 'Активно', type: 'bool' },
      { id: 'is_deleted', label: 'Удалено', type: 'bool' },
    ],
    filters: [
      { id: 'name', type: 'text', label: 'Наименование' },
      { id: 'inn', type: 'text', label: 'ИНН' },
    ],
    toolbar: {
      createHref: '/reference/legal-entities/new',
    },
    columnOverrides: {
      id: { href: (row: { id: number }) => `/reference/legal-entities/${row.id}` },
    },
  } as ListPageConfig<LegalEntityRow>,
}