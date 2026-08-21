import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { documentsConfig } from '../features/documents/config'

export function DocumentsPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={documentsConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Главная', to: '/' },
        { label: 'Документы' },
      ]}
    />
  )
}
