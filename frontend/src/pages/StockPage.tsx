import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { stockConfig } from '../features/stock/config'

export function StockPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={stockConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Склад', to: '/' },
        { label: 'Остатки' },
      ]}
    />
  )
}
