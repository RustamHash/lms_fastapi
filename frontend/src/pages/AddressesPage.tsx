import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AssignDeliveryZoneDialog } from '../features/addresses/AssignDeliveryZoneDialog'
import { addressConfig } from '../features/addresses/config'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import type { GroupActionContext } from '../features/entity-system/types'

type AssignDialogState = {
  addressIds: number[]
  context: GroupActionContext<{ id: number }>
}

export function AddressesPage() {
  const navigate = useNavigate()
  const [assignDialog, setAssignDialog] = useState<AssignDialogState | null>(null)

  const config = useMemo(
    () => ({
      ...addressConfig.list,
      groupActions: [
        {
          id: 'assign-zone',
          label: 'Назначить зону',
          icon: '🗺️',
          action: async (
            rows: { id: number }[],
            context: GroupActionContext<{ id: number }>,
          ) => {
            setAssignDialog({ addressIds: rows.map((row) => row.id), context })
          },
        },
      ],
    }),
    [],
  )

  return (
    <>
      <EntityListPage
        config={config}
        onBack={() => navigate('/references')}
        breadcrumbs={[
          { label: 'Справочники', to: '/references' },
          { label: 'Адреса' },
        ]}
      />
      {assignDialog ? (
        <AssignDeliveryZoneDialog
          addressIds={assignDialog.addressIds}
          onCancel={() => setAssignDialog(null)}
          onComplete={(message) => {
            assignDialog.context.notify(message, 'success')
            assignDialog.context.reload()
            assignDialog.context.clearSelection()
            setAssignDialog(null)
          }}
        />
      ) : null}
    </>
  )
}
