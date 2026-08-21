import { GenericDetailPage } from '../components/GenericDetailPage'

export function DocumentDetailPage() {
  return (
    <GenericDetailPage
      title="Документ"
      apiUrl="/api/v1/documents"
      backHref="/documents"
      backLabel="← К документам"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'document_number', label: 'Номер', type: 'text' as const },
        { key: 'document_type', label: 'Тип', type: 'text' as const },
        { key: 'status', label: 'Статус', type: 'text' as const },
        { key: 'document_date', label: 'Дата документа', type: 'date' as const },
        { key: 'warehouse_id', label: 'Склад ID', type: 'number' as const },
        { key: 'is_delivery', label: 'Доставка', type: 'bool' as const },
        { key: 'is_edo', label: 'ЭДО', type: 'bool' as const },
      ]}
    />
  )
}
