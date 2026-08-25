import type { ListPageConfig } from '../entity-system/types'

type TariffDocumentRow = {
  id: number
  contract_id: number
  document_type: string
  number: string
  date: string
  valid_from: string
  valid_until: string | null
  currency: string
  vat_rate: string
}

export const tariffDocumentsConfig: ListPageConfig<TariffDocumentRow> = {
  entityKey: 'tariff_documents',
  title: 'Документы тарифов',
  apiUrl: '/api/v1/tariff-documents',
  listPath: '/reference/tariff-documents',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'number', label: 'Номер', type: 'text' },
    { id: 'document_type', label: 'Тип документа', type: 'text' },
    { id: 'contract_id', label: 'Договор ID', type: 'number' },
    { id: 'date', label: 'Дата', type: 'date' },
    { id: 'valid_from', label: 'Действует с', type: 'date' },
    { id: 'valid_until', label: 'Действует до', type: 'date' },
    { id: 'currency', label: 'Валюта', type: 'text' },
    { id: 'vat_rate', label: 'Ставка НДС', type: 'text' },
  ],
  filters: [
    { id: 'number', type: 'text', label: 'Номер' },
    { id: 'document_type', type: 'text', label: 'Тип документа' },
    { id: 'contract_id', type: 'text', label: 'Договор ID' },
  ],

  columnOverrides: {
    id: { href: (row) => `/reference/tariff-documents/${row.id}` },
  },
}