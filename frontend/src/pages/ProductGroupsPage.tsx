import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { productGroupsConfig } from '../features/product-groups/config'

export function ProductGroupsPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={productGroupsConfig}
      onBack={() => navigate('/references')}
      breadcrumbs={[
        { label: 'Справочники', to: '/references' },
        { label: 'Группы товаров' },
      ]}
    />
  )
}
