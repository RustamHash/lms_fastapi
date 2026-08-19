import type { ListPageConfig } from '../entity-list/types'

type AddressInputAliasRow = {
  id: number
  raw_text: string
  hash: string
  normalized_address_id: number
  full_address: string | null
  source: string
  created_at?: string
  updated_at?: string
  is_deleted?: boolean
}

export const addressInputAliasConfig = {
  list: {
    entityKey: 'address_input_aliases',
    title: 'Варианты ввода адресов',
    apiUrl: '/api/v1/parties/aliases',
    
    columns: [
      { id: 'id', label: 'ID', type: 'number' },
      { id: 'raw_text', label: 'Исходная строка', type: 'text' },
      { id: 'hash', label: 'Норм. ключ', type: 'text' },
      { id: 'full_address', label: 'Адрес', type: 'text' },
      { id: 'normalized_address_id', label: 'Адрес ID', type: 'number' },
      { id: 'source', label: 'Источник', type: 'text' },
    ],
    
    filters: [
      { id: 'raw_text', type: 'text', label: 'Исходная строка' },
      { id: 'full_address', type: 'text', label: 'Адрес' },
    ],
    
    toolbar: {
      showExport: true,
    },
    
    columnOverrides: {
      id: {
        href: (row) => `/reference/address-input-aliases/${row.id}`,
      },
      normalized_address_id: {
        href: (row) => `/reference/addresses/${row.normalized_address_id}`,
      },
    },
  } as ListPageConfig<AddressInputAliasRow>,
}
