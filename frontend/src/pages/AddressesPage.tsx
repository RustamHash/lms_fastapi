import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { addressConfig } from '../features/addresses/config'

export function AddressesPage() {
  const navigate = useNavigate()

  return (
    <EntityListPage
      config={addressConfig.list}
      onBack={() => navigate('/references')}
      breadcrumbs={[
        { label: 'Справочники', to: '/references' },
        { label: 'Адреса' },
      ]}
    />
  )
}
