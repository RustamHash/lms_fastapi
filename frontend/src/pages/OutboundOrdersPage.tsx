import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { ImportDialog } from '../components/ImportDialog'
import { outboundOrdersConfig } from '../features/outbound-orders/config'

export function OutboundOrdersPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
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
          onSuccess={() => {
            void queryClient.refetchQueries({
              queryKey: ['entity-system', outboundOrdersConfig.entityKey],
            })
          }}
        />
      ) : null}
    </>
  )
}
