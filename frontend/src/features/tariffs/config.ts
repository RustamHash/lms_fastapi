import type { ListPageConfig } from '../entity-list/types'

type TariffRow = {
  id: number
  document_id: number
  service_group: string
  name: string
  description: string
  unit: string
  price: string
  is_deleted: boolean
  is_active: boolean
}

export const tariffConfig = {
  list: {
    entityKey: 'tariffs',
    title: 'Тарифы',
    apiUrl: '/api/v1/parties/tariffs',
    columns: [
      { id: 'id', label: 'ID', type: 'number' },
      { id: 'name', label: 'Название', type: 'text' },
      { id: 'service_group', label: 'Группа', type: 'text' },
      { id: 'unit', label: 'Единица', type: 'text' },
      { id: 'price', label: 'Цена', type: 'number' },
      { id: 'is_active', label: 'Активен', type: 'bool' },
      { id: 'is_deleted', label: 'Удалён', type: 'bool' },
    ],
    filters: [
      { id: 'name', type: 'text', label: 'Название' },
      { id: 'service_group', type: 'text', label: 'Группа' },
    ],
    columnOverrides: {
      name: { href: (row) => `/reference/tariffs/${row.id}` },
    },
  } as ListPageConfig<TariffRow>,
}
