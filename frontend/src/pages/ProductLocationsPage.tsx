import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { productLocationsConfig } from '../features/product-locations/config'

export function ProductLocationsPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={productLocationsConfig}
      onBack={() => navigate('/references')}
      breadcrumbs={[
        { label: 'Справочники', to: '/references' },
        { label: 'Товар-ячейка' },
      ]}
    />
  )
}
