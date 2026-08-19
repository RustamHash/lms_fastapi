import { useNavigate } from 'react-router-dom'
import {
  useEffect,
  useRef,
  useState,
  type MouseEvent,
  type PointerEvent as ReactPointerEvent,
  type ReactNode,
} from 'react'
import {
  LIST_COL_WIDTH_DEFAULT,
  LIST_COL_WIDTH_MAX,
  LIST_COL_WIDTH_MIN,
  clampListColumnWidthPx,
} from '../features/lists/columnWidthConstants'
import { arrayMove } from '../lib/arrayMove'
import { excludeColumnHasActiveEntries } from '../features/lists/listExcludeFilters'
import { computeAutoFitColumnWidthPx } from '../lib/measureColumnTextWidth'
import { ListFilterCell } from './ListFilterCell'

const COL_DND_MIME = 'application/x-sslog-col-index'

const MSG_NO_RIGHTS_CREATE = 'Нет прав на создание'
const MSG_NO_CREATE_ROUTE = 'Для данной сущности создание вручную недоступно'
const MSG_EXPORT_NONE_SELECTED = 'Ничего не выбрано. Отметьте строки чекбоксами.'
const MSG_VIEW_UNAVAILABLE_DEFAULT = 'Подождите, загружаются настройки колонок.'
const MSG_RESET_NO_FILTERS = 'Нет активных фильтров'

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

function IconFilterReset() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={16} height={16} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M4 7h16M6 7l2 12h8l2-12M9 7V4h6v3" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
      <path d="M10 11l4 4m0-4l-4 4" stroke="currentColor" strokeWidth={2} strokeLinecap="round" />
    </svg>
  )
}

type ColumnFilterDef =
  | { kind: 'text' }
  | { kind: 'datetime' }
  | { kind: 'select'; options: { value: string; label: string }[] }

export type ListNoticeKind = 'success' | 'warning' | 'error' | 'info'

type Props<Row extends { id: number }> = {
  onRefresh: () => void
  createHref?: string
  canCreate?: boolean
  onExportCsv: () => void
  onOpenView: () => void
  onResetFilters: () => void
  canOpenView?: boolean
  viewUnavailableMessage?: string
  hasActiveFilters: boolean
  onNotify: (message: string, kind: ListNoticeKind) => void
  viewDialogOpen: boolean
  viewDialogTitle: string
  viewDialogHint: string
  viewDraftOrder: string[]
  isViewDraftHidden: (id: string) => boolean
  onViewDraftToggle: (id: string, visible: boolean) => void
  onViewDraftSelectAll: (visible: boolean) => void
  onViewDraftSetOrder: (order: string[]) => void
  viewDraftColumnWidth: (colId: string) => string
  onViewDraftColumnWidthChange: (colId: string, value: string) => void
  onViewSave: () => void
  onViewClose: () => void
  selectionCount: number
  visibleColumnIds: string[]
  columnLabel: (cid: string) => string
  sortCol: string | null
  sortDir: 'asc' | 'desc'
  onSortHeaderClick: (cid: string) => void
  columnFilters: Record<string, ColumnFilterDef>
  filters: Record<string, string>
  excludeFilters: Record<string, string[]>
  onFilterChange: (cid: string, next: string) => void
  loading: boolean
  rows: Row[]
  allSelected: boolean
  onToggleAll: (checked: boolean) => void
  isSelected: (id: number) => boolean
  onToggleRow: (id: number, checked: boolean) => void
  onCellContextMenu: (e: MouseEvent<HTMLTableCellElement>, row: Row, colId: string) => void
  renderCell: (row: Row, cid: string) => ReactNode
  totalRowsCount: number
  columnWidthsPx: Record<string, number>
  onCommitColumnWidth: (colId: string, widthPx: number) => void | Promise<void>
  plainCellText: (row: Row, colId: string) => string
  toolbarLeft?: ReactNode
}

export function ListTableShell<Row extends { id: number }>({
  onRefresh,
  createHref,
  canCreate = true,
  onExportCsv,
  onOpenView,
  onResetFilters,
  canOpenView = true,
  viewUnavailableMessage = MSG_VIEW_UNAVAILABLE_DEFAULT,
  hasActiveFilters,
  onNotify,
  viewDialogOpen,
  viewDialogTitle,
  viewDialogHint,
  viewDraftOrder,
  isViewDraftHidden,
  onViewDraftToggle,
  onViewDraftSelectAll,
  onViewDraftSetOrder,
  viewDraftColumnWidth,
  onViewDraftColumnWidthChange,
  onViewSave,
  onViewClose,
  selectionCount,
  visibleColumnIds,
  columnLabel,
  sortCol,
  sortDir,
  onSortHeaderClick,
  columnFilters,
  filters,
  excludeFilters,
  onFilterChange,
  loading,
  rows,
  allSelected,
  onToggleAll,
  isSelected,
  onToggleRow,
  onCellContextMenu,
  renderCell,
  totalRowsCount,
  columnWidthsPx,
  onCommitColumnWidth,
  plainCellText,
  toolbarLeft,
}: Props<Row>) {
  const navigate = useNavigate()

  const [dragColPreview, setDragColPreview] = useState<{ colId: string; widthPx: number } | null>(null)
  const colDragRef = useRef<{ colId: string; startX: number; startW: number; lastW: number } | null>(null)

  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null)
  const [draggingIndex, setDraggingIndex] = useState<number | null>(null)

  useEffect(() => {
    if (!viewDialogOpen) {
      setDragOverIndex(null)
      setDraggingIndex(null)
    }
  }, [viewDialogOpen])

  const viewAllVisible = viewDialogOpen && viewDraftOrder.length > 0 && viewDraftOrder.every((id) => !isViewDraftHidden(id))
  const viewNoneVisible = viewDialogOpen && viewDraftOrder.length > 0 && viewDraftOrder.every((id) => isViewDraftHidden(id))

  const createReady = canCreate && Boolean(createHref)
  const createMuted = !createReady

  const exportReady = selectionCount > 0
  const exportMuted = !exportReady

  const viewMuted = !canOpenView

  const resetMuted = !hasActiveFilters

  function onCreateClick() {
    if (!canCreate) {
      onNotify(MSG_NO_RIGHTS_CREATE, 'error')
      return
    }
    if (!createHref) {
      onNotify(MSG_NO_CREATE_ROUTE, 'warning')
      return
    }
    navigate(createHref)
  }

  function onExportClick() {
    if (!exportReady) {
      onNotify(MSG_EXPORT_NONE_SELECTED, 'warning')
      return
    }
    onExportCsv()
    onNotify('CSV выгружен', 'success')
  }

  function onViewClick() {
    if (!canOpenView) {
      onNotify(viewUnavailableMessage, 'info')
      return
    }
    onOpenView()
  }

  function onResetClick() {
    if (!hasActiveFilters) {
      onNotify(MSG_RESET_NO_FILTERS, 'info')
      return
    }
    onResetFilters()
    onNotify('Фильтры сброшены', 'success')
  }

  function onRefreshClick() {
    onRefresh()
  }

  function colWidthPx(cid: string): number {
    if (dragColPreview?.colId === cid) return dragColPreview.widthPx
    return columnWidthsPx[cid] ?? LIST_COL_WIDTH_DEFAULT
  }

  function onColResizePointerDown(cid: string, e: ReactPointerEvent<HTMLSpanElement>) {
    if (e.button !== 0) return
    e.preventDefault()
    e.stopPropagation()
    
    const startW = columnWidthsPx[cid] ?? LIST_COL_WIDTH_DEFAULT
    const startX = e.clientX
    colDragRef.current = { colId: cid, startX, startW, lastW: startW }
    
    // Захватываем указатель
    const grip = e.currentTarget
    grip.setPointerCapture(e.pointerId)
    setDragColPreview({ colId: cid, widthPx: startW })

    function move(ev: PointerEvent) {
      const d = colDragRef.current
      if (!d) return
      const dx = ev.clientX - d.startX
      const w = clampListColumnWidthPx(d.startW + dx)
      d.lastW = w
      setDragColPreview({ colId: d.colId, widthPx: w })
    }

    function end(ev: PointerEvent) {
      window.removeEventListener('pointermove', move)
      window.removeEventListener('pointerup', end)
      window.removeEventListener('pointercancel', end)
      
      const d = colDragRef.current
      colDragRef.current = null
      setDragColPreview(null)
      
      try {
        grip.releasePointerCapture(ev.pointerId)
      } catch {
        /* already released */
      }
      
      if (!d || ev.type === 'pointercancel') return
      if (d.lastW !== d.startW) {
        void onCommitColumnWidth(cid, d.lastW)
      }
    }

    window.addEventListener('pointermove', move)
    window.addEventListener('pointerup', end)
    window.addEventListener('pointercancel', end)
  }

  function onColResizeDoubleClick(cid: string, e: React.MouseEvent) {
    e.preventDefault()
    e.stopPropagation()
    
    const label = columnLabel(cid)
    const texts = rows.map((r) => plainCellText(r, cid))
    const w = computeAutoFitColumnWidthPx(label, texts)
    
    console.log('Автоширина для', cid, ':', w, 'px')
    
    void onCommitColumnWidth(cid, w)
  }

  return (
    <>
      <div className="list-page-toolbar-row">
        {toolbarLeft ? <div className="list-toolbar-left">{toolbarLeft}</div> : <div className="list-toolbar-left" />}
        <div className="list-toolbar">
          <div className="list-toolbar__left" />
          <div className="list-toolbar__right">
            <button type="button" className="tb tb--icon tb--refresh" onClick={onRefreshClick} aria-label="Обновить данные" title="Обновить данные">
              <IconRefresh />
            </button>
            <button type="button" className={`tb tb--icon tb--create${createMuted ? ' tb--muted' : ''}`} onClick={onCreateClick} aria-label="Создать" title="Создать">
              <IconPlus />
            </button>
            <button type="button" className={`tb tb--icon tb--excel${exportMuted ? ' tb--muted' : ''}`} onClick={onExportClick} aria-label="Экспорт CSV" title="Экспорт CSV (выделите строки)">
              <IconTableDown />
            </button>
            <button type="button" className={`tb tb--icon tb--view${viewMuted ? ' tb--muted' : ''}`} onClick={onViewClick} aria-label="Вид таблицы" title="Колонки таблицы">
              <IconColumns />
            </button>
            <button type="button" className={`tb tb--icon tb--reset${resetMuted ? ' tb--muted' : ''}`} onClick={onResetClick} aria-label="Сбросить фильтры" title="Сбросить фильтры">
              <IconFilterReset />
            </button>
          </div>
        </div>
      </div>

      <div className="list-table-area">
        <p className={`list-selection-msg${selectionCount > 0 ? ' is-active' : ''}`} role="status">
          {selectionCount > 0 ? `Выделено: ${selectionCount}` : '\u00A0'}
        </p>

        <div className="table-wrap">
          <table className="list-table list-table--col-size">
            <colgroup>
              <col className="list-table__col-cb" />
              {visibleColumnIds.map((cid) => (
                <col key={cid} style={{ width: `${colWidthPx(cid)}px` }} />
              ))}
            </colgroup>
            <thead>
              <tr className="list-table__head-row">
                <th className="list-table__cb">
                  <input type="checkbox" checked={allSelected} onChange={(e) => onToggleAll(e.target.checked)} aria-label="Выбрать все на странице" />
                </th>
                {visibleColumnIds.map((cid) => {
                  const label = columnLabel(cid)
                  const active = sortCol === cid
                  const ariaSort = active ? (sortDir === 'asc' ? 'ascending' : 'descending') : 'none'
                  return (
                    <th key={cid} aria-sort={ariaSort} className="list-table__th-col">
                      <button type="button" className="list-table__sort-btn" onClick={() => onSortHeaderClick(cid)} title={active ? (sortDir === 'asc' ? 'По убыванию' : 'По возрастанию') : 'Сортировать'}>
                        <span className="list-table__sort-label">{label}</span>
                        {active ? <span className="list-table__sort-arrow" aria-hidden>{sortDir === 'asc' ? ' ▲' : ' ▼'}</span> : null}
                      </button>
                      <span 
                        className="list-table__col-resize" 
                        role="separator" 
                        aria-orientation="vertical" 
                        aria-label={`Ширина колонки «${label}». Перетащите или двойной клик — по содержимому.`} 
                        title="Тянуть — ширина · двойной клик — по данным" 
                        onPointerDown={(e) => onColResizePointerDown(cid, e)} 
                        onDoubleClick={(e) => onColResizeDoubleClick(cid, e)}
                      />
                    </th>
                  )
                })}
              </tr>
              <tr className="list-filter-row">
                <th />
                {visibleColumnIds.map((cid) => {
                  const def = columnFilters[cid]
                  const exList = excludeFilters[cid] ?? []
                  const highlightExclude = excludeColumnHasActiveEntries(exList, def)
                  return (
                    <th key={`f-${cid}`}>
                      <ListFilterCell kind={def.kind === 'select' ? 'select' : def.kind === 'datetime' ? 'datetime' : 'text'} value={filters[cid] ?? ''} onChange={(next) => onFilterChange(cid, next)} options={def.kind === 'select' ? def.options : undefined} aria-label={`Фильтр: ${columnLabel(cid)}`} highlightActive={highlightExclude} />
                    </th>
                  )
                })}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td className="list-table__empty" colSpan={visibleColumnIds.length + 1}>Загрузка…</td>
                </tr>
              ) : totalRowsCount === 0 ? (
                <tr>
                  <td className="list-table__empty" colSpan={visibleColumnIds.length + 1} role="status">Нет записей</td>
                </tr>
              ) : rows.length === 0 ? (
                <tr>
                  <td className="list-table__empty" colSpan={visibleColumnIds.length + 1} role="status">Нет данных по текущим фильтрам. Измените условия в строке фильтров или сбросьте их кнопкой на панели над таблицей.</td>
                </tr>
              ) : (
                rows.map((row) => (
                  <tr key={row.id}>
                    <td className="list-table__cb">
                      <input type="checkbox" checked={isSelected(row.id)} onChange={(e) => onToggleRow(row.id, e.target.checked)} aria-label={`Выбрать строку ${row.id}`} />
                    </td>
                    {visibleColumnIds.map((cid) => (
                      <td key={cid} onContextMenu={(e) => onCellContextMenu(e, row, cid)}>{renderCell(row, cid)}</td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="list-table-footer" aria-live="polite">
        <span className="list-table-count">{rows.length}/{totalRowsCount}</span>
      </div>

      {viewDialogOpen ? (
        <div className="dialog-backdrop dialog-backdrop--cols" role="presentation">
          <div className="dialog dialog--column-picker" role="dialog" aria-modal="true" aria-labelledby="list-cols-title">
            <div className="dialog-column-picker__head">
              <h2 id="list-cols-title" className="dialog-column-picker__title">{viewDialogTitle}</h2>
              <p className="dialog__hint dialog-column-picker__hint">{viewDialogHint}</p>
              {viewDraftOrder.length > 0 ? (
                <div className="dialog-cols__select-all dialog-column-picker__select-all">
                  <label>
                    <input type="checkbox" checked={viewAllVisible} ref={(el) => { if (el) { el.indeterminate = viewDraftOrder.length > 0 && !viewAllVisible && !viewNoneVisible } }} onChange={(e) => onViewDraftSelectAll(e.target.checked)} />
                    Выбрать все
                  </label>
                </div>
              ) : null}
            </div>
            <div className="dialog-column-picker__scroll">
              <ul className="dialog-cols dialog-cols--in-picker">
                {viewDraftOrder.map((id, index) => (
                  <li key={id} className={`dialog-cols__row${dragOverIndex === index ? ' dialog-cols__row--drop-over' : ''}${draggingIndex === index ? ' dialog-cols__row--dragging' : ''}`} onDragOver={(e) => { e.preventDefault(); e.dataTransfer.dropEffect = 'move'; setDragOverIndex(index) }} onDragLeave={(e) => { if (!e.currentTarget.contains(e.relatedTarget as Node)) { setDragOverIndex(null) } }} onDrop={(e) => { e.preventDefault(); const raw = e.dataTransfer.getData(COL_DND_MIME) || e.dataTransfer.getData('text/plain'); const from = parseInt(raw, 10); if (!Number.isFinite(from)) return; if (from !== index) { onViewDraftSetOrder(arrayMove(viewDraftOrder, from, index)) } setDragOverIndex(null); setDraggingIndex(null) }}>
                    <span className="dialog-cols__drag-handle" draggable onDragStart={(e) => { const s = String(index); e.dataTransfer.setData(COL_DND_MIME, s); e.dataTransfer.setData('text/plain', s); e.dataTransfer.effectAllowed = 'move'; setDraggingIndex(index) }} onDragEnd={() => { setDraggingIndex(null); setDragOverIndex(null) }} aria-label="Перетащить строку" title="Перетащить">⠿</span>
                    <label className="dialog-cols__label">
                      <input type="checkbox" checked={!isViewDraftHidden(id)} onChange={(ev) => onViewDraftToggle(id, ev.target.checked)} />
                      {columnLabel(id)}
                    </label>
                    <span className="dialog-cols__width" title="Ширина в пикселях; пусто — как по умолчанию">
                      <input type="number" className="dialog-cols__width-input" min={LIST_COL_WIDTH_MIN} max={LIST_COL_WIDTH_MAX} step={1} placeholder="авто" value={viewDraftColumnWidth(id)} onChange={(ev) => onViewDraftColumnWidthChange(id, ev.target.value)} aria-label={`Ширина колонки «${columnLabel(id)}», пиксели; пусто — по умолчанию`} />
                    </span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="dialog__actions dialog-column-picker__actions">
              <button type="button" className="tb tb--create" onClick={onViewSave}>Сохранить</button>
              <button type="button" className="tb tb--reset" onClick={onViewClose}>Отмена</button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  )
}
