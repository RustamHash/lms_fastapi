import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-list/EntityListPage'
import { productsConfig } from '../features/products/config'

export function ProductsPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={productsConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Склад', to: '/' },
        { label: 'Товары' },
      ]}
    />
  )
}
