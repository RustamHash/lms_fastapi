import { GenericDetailPage } from '../components/GenericDetailPage'

export function BatchDetailPage() {
  return (
    <GenericDetailPage
      title="Партия"
      apiUrl="/api/v1/warehouse/batches"
      backHref="/reference/batches"
      backLabel="← К партиям"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'product_id', label: 'Товар ID', type: 'number' as const },
        { key: 'batch_number', label: 'Номер партии', type: 'text' as const },
        { key: 'production_date', label: 'Дата производства', type: 'date' as const },
        { key: 'expiration_date', label: 'Срок годности', type: 'date' as const },
      ]}
    />
  )
}
