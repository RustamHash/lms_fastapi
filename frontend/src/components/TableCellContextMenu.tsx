import { createPortal } from 'react-dom'

type Props = {
  x: number
  y: number
  onOpen: () => void
  onOpenInNewTab: () => void
  onFilterByValue: () => void
  onExcludeValue: () => void
  onResetColumnFilter: () => void
  onResetAllFilters: () => void
  canOpen: boolean
  canResetColumn: boolean
  canResetAll: boolean
  onClose: () => void
}

export function TableCellContextMenu({
  x,
  y,
  onOpen,
  onOpenInNewTab,
  onFilterByValue,
  onExcludeValue,
  onResetColumnFilter,
  onResetAllFilters,
  canOpen,
  canResetColumn,
  canResetAll,
  onClose,
}: Props) {
  return createPortal(
    <>
      <div
        className="row-context-menu__backdrop"
        role="presentation"
        aria-hidden
        onClick={onClose}
        onContextMenu={(e) => e.preventDefault()}
      />
      <div
        className="row-context-menu"
        role="menu"
        style={{ left: x, top: y }}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          type="button"
          className="row-context-menu__item"
          role="menuitem"
          onClick={canOpen ? onOpen : undefined}
          disabled={!canOpen}
        >
          Открыть
        </button>
        <button
          type="button"
          className="row-context-menu__item"
          role="menuitem"
          onClick={canOpen ? onOpenInNewTab : undefined}
          disabled={!canOpen}
        >
          Открыть в новой вкладке
        </button>

        <hr className="row-context-menu__divider" />

        <button
          type="button"
          className="row-context-menu__item"
          role="menuitem"
          onClick={onFilterByValue}
        >
          Фильтр по этому значению
        </button>
        <button
          type="button"
          className="row-context-menu__item"
          role="menuitem"
          onClick={onExcludeValue}
        >
          Исключить выбранное значение
        </button>

        <hr className="row-context-menu__divider" />

        <button
          type="button"
          className="row-context-menu__item"
          role="menuitem"
          onClick={canResetColumn ? onResetColumnFilter : undefined}
          disabled={!canResetColumn}
        >
          Сбросить фильтр
        </button>
        <button
          type="button"
          className="row-context-menu__item"
          role="menuitem"
          onClick={canResetAll ? onResetAllFilters : undefined}
          disabled={!canResetAll}
        >
          Сбросить все фильтры
        </button>
      </div>
    </>,
    document.body,
  )
}