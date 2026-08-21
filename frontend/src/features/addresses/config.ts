import type { ListPageConfig } from '../entity-system/types'

type AddressRow = {
  id: number
  region: string
  city: string
  street: string
  house: string
  building: string
  structure: string
  flat: string
  postal_code: string
  full_address: string
  delivery_zone_id: number | null
  fias_id: string
  latitude: string | null
  longitude: string | null
  is_deleted: boolean
  is_active: boolean
}

export const addressConfig = {
  list: {
    entityKey: 'addresses',
    title: 'Адреса',
    apiUrl: '/api/v1/parties/addresses',
    
    columns: [
      { id: 'id', label: 'ID', type: 'number' },
      { id: 'full_address', label: 'Адрес', type: 'text' },
      { id: 'region', label: 'Регион', type: 'text' },
      { id: 'city', label: 'Город', type: 'text' },
      { id: 'street', label: 'Улица', type: 'text' },
      { id: 'house', label: 'Дом', type: 'text' },
      { id: 'postal_code', label: 'Индекс', type: 'text' },
      { id: 'delivery_zone_id', label: 'Зона доставки', type: 'number' },
      { id: 'latitude', label: 'Широта', type: 'number' },
      { id: 'longitude', label: 'Долгота', type: 'number' },
      { id: 'is_active', label: 'Активен', type: 'bool' },
      { id: 'is_deleted', label: 'Удалён', type: 'bool' },
    ],
    
    filters: [
      { id: 'full_address', type: 'text', label: 'Адрес' },
      { id: 'city', type: 'text', label: 'Город' },
      { id: 'street', type: 'text', label: 'Улица' },
      { id: 'is_deleted', type: 'bool', label: 'Удалён' },
    ],
    
    toolbar: {
      showExport: true,
    },
    
    columnOverrides: {
      full_address: {
        href: (row) => `/reference/addresses/${row.id}`,
      },
    },
  } as ListPageConfig<AddressRow>,
}
