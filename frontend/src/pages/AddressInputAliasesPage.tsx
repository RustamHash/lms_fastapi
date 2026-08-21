import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { addressInputAliasConfig } from '../features/addresses/addressInputAliasConfig'

export function AddressInputAliasesPage() {
  const navigate = useNavigate()

  return (
    <EntityListPage
      config={addressInputAliasConfig.list}
      onBack={() => navigate('/references')}
      breadcrumbs={[
        { label: 'Справочники', to: '/references' },
        { label: 'Варианты ввода' },
      ]}
    />
  )
}
