import type { ListPageConfig } from '../entity-list/types'

type TradePointRow = {
  id: number
  client_id: number
  address_id: number
  name: string
  is_deleted: boolean
  is_active: boolean
}

export const tradePointConfig = {
  list: {
    entityKey: 'trade_points',
    title: 'Торговые точки',
    apiUrl: '/api/v1/parties/trade-points',
    columns: [
      { id: 'id', label: 'ID', type: 'number' },
      { id: 'name', label: 'Название', type: 'text' },
      { id: 'client_id', label: 'Клиент ID', type: 'number' },
      { id: 'address_id', label: 'Адрес ID', type: 'number' },
      { id: 'is_active', label: 'Активна', type: 'bool' },
      { id: 'is_deleted', label: 'Удалена', type: 'bool' },
    ],
    filters: [
      { id: 'name', type: 'text', label: 'Название' },
    ],
    toolbar: {
      createHref: '/reference/trade-points/new',
    },
    columnOverrides: {
      name: { href: (row) => `/reference/trade-points/${row.id}` },
    },
  } as ListPageConfig<TradePointRow>,
}
