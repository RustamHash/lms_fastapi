import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { ImportDialog } from '../components/ImportDialog'
import { inboundOrdersConfig } from '../features/inbound-orders/config'

export function InboundOrdersPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
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
          onSuccess={() => {
            void queryClient.refetchQueries({
              queryKey: ['entity-system', inboundOrdersConfig.entityKey],
            })
          }}
        />
      ) : null}
    </>
  )
}
