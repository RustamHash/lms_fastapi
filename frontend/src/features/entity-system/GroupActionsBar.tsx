import { useState, type ReactNode } from 'react'
import type { GroupAction, GroupActionContext } from './types'

type Props<Row> = {
  actions: GroupAction<Row>[]
  selectedRows: Row[]
  context: GroupActionContext<Row>
}

export function GroupActionsBar<Row>({ actions, selectedRows, context }: Props<Row>) {
  const [confirmAction, setConfirmAction] = useState<GroupAction<Row> | null>(null)
  const [executing, setExecuting] = useState<string | null>(null)

  const availableActions = actions.filter((action) => {
    if (selectedRows.length === 0) return false
    if (action.maxSelection && selectedRows.length > action.maxSelection) return false
    if (action.condition && !action.condition(selectedRows)) return false
    return true
  })

  if (availableActions.length === 0) return null

  async function executeAction(action: GroupAction<Row>) {
    setExecuting(action.id)
    try {
      await action.action(selectedRows, context)
    } finally {
      setExecuting(null)
      setConfirmAction(null)
    }
  }

  return (
    <>
      <div className="list-toolbar__group" role="group" aria-label="Групповые действия">
        {availableActions.map((action) => (
          <button
            key={action.id}
            type="button"
            className={`tb tb--icon tb--group${
              executing === action.id || (action.disabled?.(selectedRows) ?? false)
                ? ' tb--muted'
                : ''
            }`}
            disabled={
              executing === action.id || (action.disabled?.(selectedRows) ?? false)
            }
            onClick={() => {
              if (action.confirmMessage) {
                setConfirmAction(action)
              } else {
                void executeAction(action)
              }
            }}
            aria-label={action.label}
            title={action.label}
          >
            {executing === action.id ? (
              <span className="tb__spinner" aria-hidden />
            ) : (
              (action.icon ?? <DefaultGroupIcon />)
            )}
          </button>
        ))}
      </div>

      {confirmAction ? (
        <div className="dialog-backdrop" role="presentation">
          <div className="dialog" role="dialog" aria-modal="true">
            <h3 className="dialog__title">Подтверждение</h3>
            <p className="dialog__text">
              {typeof confirmAction.confirmMessage === 'function'
                ? confirmAction.confirmMessage(selectedRows)
                : confirmAction.confirmMessage}
            </p>
            <div className="dialog__actions">
              <button
                type="button"
                className="tb tb--create"
                onClick={() => void executeAction(confirmAction)}
              >
                Подтвердить
              </button>
              <button
                type="button"
                className="tb tb--reset"
                onClick={() => setConfirmAction(null)}
              >
                Отмена
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  )
}

function DefaultGroupIcon(): ReactNode {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={16} height={16} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M9 11l3 3L22 4"
        stroke="currentColor"
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"
        stroke="currentColor"
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}
