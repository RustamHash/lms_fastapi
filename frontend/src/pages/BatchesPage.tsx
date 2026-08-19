import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-list/EntityListPage'
import { batchesConfig } from '../features/batches/config'

export function BatchesPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={batchesConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Склад', to: '/' },
        { label: 'Партии' },
      ]}
    />
  )
}
