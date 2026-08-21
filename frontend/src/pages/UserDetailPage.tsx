import { GenericDetailPage } from '../components/GenericDetailPage'

export function UserDetailPage() {
  return (
    <GenericDetailPage
      title="Пользователь"
      apiUrl="/api/v1/users"
      backHref="/users"
      backLabel="← К пользователям"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'username', label: 'Имя', type: 'text' as const },
        { key: 'phone', label: 'Телефон', type: 'text' as const },
        { key: 'email', label: 'Email', type: 'text' as const },
        { key: 'is_superuser', label: 'Суперпользователь', type: 'bool' as const },
        { key: 'is_active', label: 'Активен', type: 'bool' as const },
      ]}
    />
  )
}
