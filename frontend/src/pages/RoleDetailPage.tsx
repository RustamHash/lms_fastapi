import { GenericDetailPage } from '../components/GenericDetailPage'

export function RoleDetailPage() {
  return (
    <GenericDetailPage
      title="Роль"
      apiUrl="/api/v1/roles"
      backHref="/roles"
      backLabel="← К ролям"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'name', label: 'Название', type: 'text' as const },
        { key: 'code', label: 'Код', type: 'text' as const },
      ]}
    />
  )
}
