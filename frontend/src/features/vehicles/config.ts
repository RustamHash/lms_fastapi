import type { ListPageConfig } from '../entity-system/types'

type VehicleRow = {
  id: number
  number: string
  brand: string
  model: string
  capacity: number | null
  volume: number | null
  carrier_id: number | null
}

export const vehiclesConfig: ListPageConfig<VehicleRow> = {
  entityKey: 'vehicles',
  title: 'Транспорт',
  apiUrl: '/api/v1/delivery/vehicles',
  listPath: '/reference/vehicles',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'number', label: 'Гос. номер', type: 'text' },
    { id: 'brand', label: 'Марка', type: 'text' },
    { id: 'model', label: 'Модель', type: 'text' },
    { id: 'capacity', label: 'Грузоподъёмность', type: 'number' },
    { id: 'volume', label: 'Объём', type: 'number' },
  ],
  filters: [
    { id: 'number', type: 'text', label: 'Гос. номер' },
    { id: 'brand', type: 'text', label: 'Марка' },
  ],

  columnOverrides: {
    id: { href: (row) => `/reference/vehicles/${row.id}` },
  },
}