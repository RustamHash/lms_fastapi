import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { auditConfig } from '../features/audit/config'

export function AuditPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={auditConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Главная', to: '/' },
        { label: 'Аудит' },
      ]}
    />
  )
}
