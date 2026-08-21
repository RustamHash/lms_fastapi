import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { tariffDocumentsConfig } from '../features/tariff-documents/config'

export function TariffDocumentsPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={tariffDocumentsConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Справочники', to: '/references' },
        { label: 'Документы тарифов' },
      ]}
    />
  )
}
