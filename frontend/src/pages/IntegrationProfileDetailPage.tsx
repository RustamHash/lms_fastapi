import { GenericDetailPage } from '../components/GenericDetailPage'

export function IntegrationProfileDetailPage() {
  return (
    <GenericDetailPage
      title="Профиль интеграции"
      apiUrl="/api/v1/integrations/profiles"
      backHref="/integrations/profiles"
      backLabel="← К профилям"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'depositor_id', label: 'Поклажедатель ID', type: 'number' as const },
        { key: 'name', label: 'Название', type: 'text' as const },
        { key: 'source_type', label: 'Тип источника', type: 'text' as const },
      ]}
    />
  )
}
