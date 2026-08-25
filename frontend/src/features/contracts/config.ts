import type { ListPageConfig } from '../entity-system/types'

type ContractRow = {
  id: number
  number: string
  customer_id: number
  executor_id: number
  contract_type: string
  start_date: string
  end_date: string | null
  status: string
  is_deleted: boolean
  is_active: boolean
}

export const contractConfig = {
  list: {
    entityKey: 'contracts',
    title: 'Договоры',
    apiUrl: '/api/v1/contracts',
    listPath: '/reference/contracts',
    columns: [
      { id: 'id', label: 'ID', type: 'number' },
      { id: 'number', label: 'Номер', type: 'text' },
      { id: 'contract_type', label: 'Тип', type: 'text' },
      { id: 'start_date', label: 'Начало', type: 'date' },
      { id: 'end_date', label: 'Окончание', type: 'date' },
      { id: 'status', label: 'Статус', type: 'text' },
      { id: 'is_active', label: 'Активен', type: 'bool' },
      { id: 'is_deleted', label: 'Удалён', type: 'bool' },
    ],
    filters: [
      { id: 'number', type: 'text', label: 'Номер' },
      { id: 'status', type: 'text', label: 'Статус' },
    ],
    toolbar: {
      createHref: '/reference/contracts/new',
    },
    columnOverrides: {
      id: { href: (row: { id: number }) => `/reference/contracts/${row.id}` },
    },
  } as ListPageConfig<ContractRow>,
}