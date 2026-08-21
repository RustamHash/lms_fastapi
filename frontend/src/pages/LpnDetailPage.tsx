import { GenericDetailPage } from '../components/GenericDetailPage'

export function LpnDetailPage() {
  return (
    <GenericDetailPage
      title="LPN"
      apiUrl="/api/v1/warehouse/lpns"
      backHref="/reference/lpns"
      backLabel="← К LPN"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'number', label: 'Номер', type: 'text' as const },
        { key: 'status', label: 'Статус', type: 'text' as const },
      ]}
    />
  )
}
