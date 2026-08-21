import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { ImportDialog } from '../components/ImportDialog'
import { inboundOrdersConfig } from '../features/inbound-orders/config'

export function InboundOrdersPage() {
  const navigate = useNavigate()
  const [importOpen, setImportOpen] = useState(false)
  
  return (
    <>
      <EntityListPage
        config={inboundOrdersConfig}
        onBack={() => navigate('/orders')}
        onImport={() => setImportOpen(true)}
        breadcrumbs={[
          { label: 'Главная', to: '/' },
          { label: 'Заказы', to: '/orders' },
          { label: 'Входящие' },
        ]}
      />
      
      {importOpen ? (
        <ImportDialog
          documentType="porder"
          title="Импорт приходных заказов"
          onClose={() => setImportOpen(false)}
        />
      ) : null}
    </>
  )
}
