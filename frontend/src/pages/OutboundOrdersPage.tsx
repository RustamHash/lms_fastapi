import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { ImportDialog } from '../components/ImportDialog'
import { outboundOrdersConfig } from '../features/outbound-orders/config'

export function OutboundOrdersPage() {
  const navigate = useNavigate()
  const [importOpen, setImportOpen] = useState(false)
  
  return (
    <>
      <EntityListPage
        config={outboundOrdersConfig}
        onBack={() => navigate('/orders')}
        onImport={() => setImportOpen(true)}
        breadcrumbs={[
          { label: 'Главная', to: '/' },
          { label: 'Заказы', to: '/orders' },
          { label: 'Исходящие' },
        ]}
      />
      
      {importOpen ? (
        <ImportDialog
          documentType="order"
          title="Импорт расходных заказов"
          onClose={() => setImportOpen(false)}
        />
      ) : null}
    </>
  )
}
