import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { lpnsConfig } from '../features/lpns/config'

export function LpnsPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={lpnsConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Справочники', to: '/references' },
        { label: 'LPN' },
      ]}
    />
  )
}
