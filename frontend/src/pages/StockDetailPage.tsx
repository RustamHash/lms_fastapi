import { GenericDetailPage } from '../components/GenericDetailPage'

export function StockDetailPage() {
  return (
    <GenericDetailPage
      title="Остаток"
      apiUrl="/api/v1/warehouse/stock"
      backHref="/stock"
      backLabel="← К остаткам"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'product_id', label: 'Товар ID', type: 'number' as const },
        { key: 'location_id', label: 'Ячейка ID', type: 'number' as const },
        { key: 'lpn_id', label: 'LPN ID', type: 'number' as const },
        { key: 'batch_id', label: 'Партия ID', type: 'number' as const },
        { key: 'quantity', label: 'Количество', type: 'text' as const },
        { key: 'reserved_quantity', label: 'Зарезервировано', type: 'text' as const },
      ]}
    />
  )
}
