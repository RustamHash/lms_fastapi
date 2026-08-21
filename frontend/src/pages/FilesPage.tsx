import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { filesConfig } from '../features/files/config'

export function FilesPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={filesConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Главная', to: '/' },
        { label: 'Файлы' },
      ]}
    />
  )
}
