import type { ListPageConfig } from '../entity-system/types'

type DocumentRow = {
  id: number
  document_number: string
  document_date: string | null
  delivery_date: string | null
  document_type: string
  contract_id: number | null
  trade_point_id: number | null
  warehouse_id: number
  virtual_warehouse_id: number | null
  status: string
  is_delivery: boolean
  is_edo: boolean
}

export const documentsConfig: ListPageConfig<DocumentRow> = {
  entityKey: 'documents',
  title: 'Документы',
  apiUrl: '/api/v1/documents',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'document_number', label: 'Номер', type: 'text' },
    { id: 'document_type', label: 'Тип', type: 'text' },
    { id: 'status', label: 'Статус', type: 'text' },
    { id: 'document_date', label: 'Дата документа', type: 'date' },
    { id: 'warehouse_id', label: 'Склад ID', type: 'number' },
    { id: 'is_delivery', label: 'Доставка', type: 'bool' },
  ],
  filters: [
    { id: 'document_number', type: 'text', label: 'Номер' },
    { id: 'document_type', type: 'text', label: 'Тип' },
    { id: 'status', type: 'text', label: 'Статус' },
  ],

  columnOverrides: {
    id: { href: (row) => `/reference/documents/${row.id}` },
  },
}