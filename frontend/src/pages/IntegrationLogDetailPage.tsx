import { GenericDetailPage } from '../components/GenericDetailPage'

export function IntegrationLogDetailPage() {
  return (
    <GenericDetailPage
      title="Лог интеграции"
      apiUrl="/api/v1/integrations/logs"
      backHref="/integrations/logs"
      backLabel="← К логам"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'profile_id', label: 'Профиль ID', type: 'number' as const },
        { key: 'status', label: 'Статус', type: 'text' as const },
        { key: 'total_rows', label: 'Всего строк', type: 'number' as const },
        { key: 'success_rows', label: 'Успешно', type: 'number' as const },
        { key: 'error_rows', label: 'Ошибок', type: 'number' as const },
      ]}
    />
  )
}
