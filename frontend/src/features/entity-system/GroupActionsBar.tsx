import { useState } from 'react'
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
    <div className="group-actions-bar">
      <span className="group-actions-bar__count">
        Выбрано: {selectedRows.length}
      </span>
      
      {availableActions.map((action) => (
        <button
          key={action.id}
          className="group-actions-bar__button"
          disabled={
            executing === action.id ||
            (action.disabled?.(selectedRows) ?? false)
          }
          onClick={() => {
            if (action.confirmMessage) {
              setConfirmAction(action)
            } else {
              void executeAction(action)
            }
          }}
          title={action.label}
        >
          {action.icon}
          <span>{action.label}</span>
          {executing === action.id ? (
            <span className="group-actions-bar__spinner">…</span>
          ) : null}
        </button>
      ))}
      
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
    </div>
  )
}
