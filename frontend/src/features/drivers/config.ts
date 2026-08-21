import type { ListPageConfig } from '../entity-system/types'

type DriverRow = {
  id: number
  name: string
  phone: string
  carrier_id: number | null
}

export const driversConfig: ListPageConfig<DriverRow> = {
  entityKey: 'drivers',
  title: 'Водители',
  apiUrl: '/api/v1/delivery/drivers',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'name', label: 'ФИО', type: 'text' },
    { id: 'phone', label: 'Телефон', type: 'text' },
    { id: 'carrier_id', label: 'Перевозчик ID', type: 'number' },
  ],
  filters: [
    { id: 'name', type: 'text', label: 'ФИО' },
    { id: 'phone', type: 'text', label: 'Телефон' },
  ],
}
