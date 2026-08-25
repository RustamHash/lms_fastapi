import type { ListPageConfig } from '../entity-system/types'

type DeliveryZoneRow = {
  id: number
  name: string
  is_deleted: boolean
  is_active: boolean
}

export const deliveryZoneConfig = {
  list: {
    entityKey: 'delivery_zones',
    title: 'Зоны доставки',
    apiUrl: '/api/v1/delivery-zones',
    listPath: '/reference/delivery-zones',
    
    columns: [
      { id: 'id', label: 'ID', type: 'number' },
      { id: 'name', label: 'Название', type: 'text' },
      { id: 'is_active', label: 'Активна', type: 'bool' },
      { id: 'is_deleted', label: 'Удалена', type: 'bool' },
    ],
    
    filters: [
      { id: 'name', type: 'text', label: 'Название' },
    ],
    
    toolbar: {
      createHref: '/reference/delivery-zones/new',
    },
    columnOverrides: {
      id: { href: (row) => `/reference/delivery-zones/${row.id}` },
    },
  } as ListPageConfig<DeliveryZoneRow>,
}