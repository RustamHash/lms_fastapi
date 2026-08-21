import { memo, type ReactNode } from 'react'

type Props = {
  onRefresh: () => void
  onCreate: () => void
  onImport?: () => void
  onExport: () => void
  onOpenView: () => void
  onResetFilters: () => void
  canCreate: boolean
  canExport: boolean
  canOpenView: boolean
  canResetFilters: boolean
  refreshing: boolean
  toolbarLeft?: ReactNode
  onInvertSelection?: () => void
  selectionCount: number
}

function IconRefresh() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={16} height={16} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
      <path d="M3 3v5h5" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
      <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
      <path d="M21 21v-5h-5" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function IconPlus() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={16} height={16} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth={2} strokeLinecap="round" />
    </svg>
  )
}

function IconTableDown() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={16} height={16} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M4 5h16v14H4V5zm0 5h16M9 5v14" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
      <path d="M12 15v3m0 0l2.5-2.5M12 18l-2.5-2.5" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function IconColumns() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={16} height={16} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M4 4h5v16H4V4zm11 0h5v7h-5V4zm0 9h5v7h-5v-7z" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function IconImport() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={16} height={16} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M12 3v12m0 0l-4-4m4 4l4-4" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
      <path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function IconFilterReset() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={16} height={16} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M4 7h16M6 7l2 12h8l2-12M9 7V4h6v3" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
      <path d="M10 11l4 4m0-4l-4 4" stroke="currentColor" strokeWidth={2} strokeLinecap="round" />
    </svg>
  )
}

function TableToolbarInner({
  onRefresh,
  onCreate,
  onImport,
  onExport,
  onOpenView,
  onResetFilters,
  canCreate,
  canExport,
  canOpenView,
  canResetFilters,
  refreshing,
  toolbarLeft,
  onInvertSelection,
  selectionCount,
}: Props) {
  return (
    <div className="list-page-toolbar-row">
      {toolbarLeft ? <div className="list-toolbar-left">{toolbarLeft}</div> : <div className="list-toolbar-left" />}
      <div className="list-toolbar">
        <div className="list-toolbar__right">
          <button
            type="button"
            className={`tb tb--icon tb--refresh${refreshing ? ' tb--loading' : ''}`}
            onClick={onRefresh}
            aria-label="Обновить данные"
            title="Обновить данные"
            disabled={refreshing}
          >
            {refreshing ? <span className="tb__spinner" aria-hidden /> : <IconRefresh />}
          </button>
          <button
            type="button"
            className={`tb tb--icon tb--create${!canCreate ? ' tb--muted' : ''}`}
            onClick={onCreate}
            aria-label="Создать"
            title="Создать"
          >
            <IconPlus />
          </button>
          {onImport ? (
            <button type="button" className="tb tb--icon tb--import" onClick={onImport} aria-label="Импорт" title="Импорт">
              <IconImport />
            </button>
          ) : null}
          <button
            type="button"
            className={`tb tb--icon tb--excel${!canExport ? ' tb--muted' : ''}`}
            onClick={onExport}
            aria-label="Экспорт CSV"
            title="Экспорт CSV (выделите строки)"
          >
            <IconTableDown />
          </button>
          <button
            type="button"
            className={`tb tb--icon tb--view${!canOpenView ? ' tb--muted' : ''}`}
            onClick={onOpenView}
            aria-label="Вид таблицы"
            title="Колонки таблицы"
          >
            <IconColumns />
          </button>
          <button
            type="button"
            className={`tb tb--icon tb--reset${!canResetFilters ? ' tb--muted' : ''}`}
            onClick={onResetFilters}
            aria-label="Сбросить фильтры"
            title="Сбросить фильтры"
          >
            <IconFilterReset />
          </button>
          {onInvertSelection ? (
            <button
              type="button"
              className={`tb tb--icon${selectionCount === 0 ? ' tb--muted' : ''}`}
              onClick={onInvertSelection}
              aria-label="Инвертировать выделение"
              title="Инвертировать выделение"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width={16} height={16} viewBox="0 0 24 24" fill="none" aria-hidden>
                <path d="M8 3L4 7l4 4" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                <path d="M4 7h11a5 5 0 0 1 0 10h-1" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                <path d="M16 21l4-4-4-4" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          ) : null}
        </div>
      </div>
    </div>
  )
}

export const TableToolbar = memo(TableToolbarInner)
