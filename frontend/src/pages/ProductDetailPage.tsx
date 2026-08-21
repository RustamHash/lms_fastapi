import { GenericDetailPage } from '../components/GenericDetailPage'

export function ProductDetailPage() {
  return (
    <GenericDetailPage
      title="Товар"
      apiUrl="/api/v1/warehouse/products"
      backHref="/reference/products"
      backLabel="← К товарам"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'name', label: 'Название', type: 'text' as const },
        { key: 'sku', label: 'SKU', type: 'text' as const },
        { key: 'external_id', label: 'Внешний ID', type: 'text' as const },
        { key: 'depositor_id', label: 'Поклажедатель ID', type: 'number' as const },
        { key: 'weight', label: 'Вес', type: 'text' as const },
        { key: 'volume', label: 'Объём', type: 'text' as const },
        { key: 'price', label: 'Цена', type: 'text' as const },
        { key: 'is_marked', label: 'Маркировка', type: 'bool' as const },
      ]}
    />
  )
}
