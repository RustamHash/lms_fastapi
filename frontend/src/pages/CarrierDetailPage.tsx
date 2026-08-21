import { GenericDetailPage } from '../components/GenericDetailPage'

export function CarrierDetailPage() {
  return (
    <GenericDetailPage
      title="Перевозчик"
      apiUrl="/api/v1/carriers"
      backHref="/carriers"
      backLabel="← К перевозчикам"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'name', label: 'Название', type: 'text' as const },
        { key: 'phone', label: 'Телефон', type: 'text' as const },
        { key: 'email', label: 'Email', type: 'text' as const },
        { key: 'is_active', label: 'Активен', type: 'bool' as const },
      ]}
    />
  )
}
