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
          icon: (
            <svg xmlns="http://www.w3.org/2000/svg" width={16} height={16} viewBox="0 0 24 24" fill="none" aria-hidden>
              <path
                d="M12 21s7-4.5 7-11a7 7 0 1 0-14 0c0 6.5 7 11 7 11z"
                stroke="currentColor"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <circle cx="12" cy="10" r="2.5" stroke="currentColor" strokeWidth={2} />
            </svg>
          ),
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
