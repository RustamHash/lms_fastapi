import { useNavigate } from 'react-router-dom'
import {
  memo,
  useEffect,
  useRef,
  useState,
  type MouseEvent,
  type PointerEvent as ReactPointerEvent,
  type ReactNode,
} from 'react'
import {
  LIST_COL_WIDTH_DEFAULT,
  clampListColumnWidthPx,
} from '../features/lists/columnWidthConstants'
import { arrayMove } from '../lib/arrayMove'
import { excludeColumnHasActiveEntries } from '../features/lists/listExcludeFilters'
import { computeAutoFitColumnWidthPx } from '../lib/measureColumnTextWidth'
import { TableToolbar } from './table/TableToolbar'
import { TableHeader } from './table/TableHeader'
import { TableFilterRow } from './table/TableFilterRow'
import { TableBody } from './table/TableBody'
import { TableFooter } from './table/TableFooter'

const COL_DND_MIME = 'application/x-sslog-col-index'

const MSG_NO_RIGHTS_CREATE = 'Нет прав на создание'
const MSG_NO_CREATE_ROUTE = 'Для данной сущности создание вручную недоступно'
const MSG_EXPORT_NONE_SELECTED = 'Ничего не выбрано. Отметьте строки чекбоксами.'
const MSG_VIEW_UNAVAILABLE_DEFAULT = 'Подождите, загружаются настройки колонок.'
const MSG_RESET_NO_FILTERS = 'Нет активных фильтров'

export type ColumnFilterDef =
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
  onRowDoubleClick?: (row: Row) => void
  onInvertSelection?: () => void
  onImport?: () => void
  filtersBar?: ReactNode
  toolbarExtra?: ReactNode
}

function ListTableShellInner<Row extends { id: number }>({
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
  onRowDoubleClick,
  onInvertSelection,
  onImport,
  filtersBar,
  toolbarExtra,
}: Props<Row>) {
  const navigate = useNavigate()

  const [dragColPreview, setDragColPreview] = useState<{ colId: string; widthPx: number } | null>(null)
  const colDragRef = useRef<{ colId: string; startX: number; startW: number; lastW: number } | null>(null)

  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null)
  const [draggingIndex, setDraggingIndex] = useState<number | null>(null)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    if (!viewDialogOpen) {
      const timer = setTimeout(() => {
        setDragOverIndex(null)
        setDraggingIndex(null)
      }, 0)
      return () => clearTimeout(timer)
    }
  }, [viewDialogOpen])

  const viewAllVisible = viewDialogOpen && viewDraftOrder.length > 0 && viewDraftOrder.every((id) => !isViewDraftHidden(id))
  const viewNoneVisible = viewDialogOpen && viewDraftOrder.length > 0 && viewDraftOrder.every((id) => isViewDraftHidden(id))

  const createReady = canCreate && Boolean(createHref)
  const exportReady = selectionCount > 0

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

  async function onRefreshClick() {
    setRefreshing(true)
    try {
      await onRefresh()
    } finally {
      setRefreshing(false)
    }
  }

  function onColResizePointerDown(cid: string, e: ReactPointerEvent<HTMLSpanElement>) {
    if (e.button !== 0) return
    e.preventDefault()
    e.stopPropagation()
    
    const startW = columnWidthsPx[cid] ?? LIST_COL_WIDTH_DEFAULT
    const startX = e.clientX
    colDragRef.current = { colId: cid, startX, startW, lastW: startW }
    
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
    
    void onCommitColumnWidth(cid, w)
  }

  return (
    <>
      <TableToolbar
        onRefresh={onRefreshClick}
        onCreate={onCreateClick}
        onImport={onImport}
        onExport={onExportClick}
        onOpenView={onViewClick}
        onResetFilters={onResetClick}
        canCreate={createReady}
        canExport={exportReady}
        canOpenView={!viewMuted}
        canResetFilters={!resetMuted}
        refreshing={refreshing}
        toolbarLeft={toolbarLeft}
        onInvertSelection={onInvertSelection}
        selectionCount={selectionCount}
        toolbarExtra={toolbarExtra}
      />

      <div className="list-table-area">
        <div className="list-table-top-row">
          <div className="list-selection-block">
            {selectionCount > 0 ? (
              <span className="list-selection-msg is-active" role="status">
                Выделено: {selectionCount}
              </span>
            ) : null}
          </div>
          
          {filtersBar ? (
            <div className="list-filters-bar-sticky">
              {filtersBar}
            </div>
          ) : null}
        </div>

        <div className="table-wrap">
          <table className="list-table list-table--col-size">
            <TableHeader
              visibleColumnIds={visibleColumnIds}
              columnLabel={columnLabel}
              sortCol={sortCol}
              sortDir={sortDir}
              onSortHeaderClick={onSortHeaderClick}
              columnWidthsPx={columnWidthsPx}
              onColResizePointerDown={onColResizePointerDown}
              onColResizeDoubleClick={onColResizeDoubleClick}
              dragColPreview={dragColPreview}
              colDragRef={colDragRef}
              allSelected={allSelected}
              onToggleAll={onToggleAll}
            />
            <TableFilterRow
              visibleColumnIds={visibleColumnIds}
              columnFilters={columnFilters}
              filters={filters}
              excludeFilters={excludeFilters}
              onFilterChange={onFilterChange}
              columnLabel={columnLabel}
              excludeColumnHasActiveEntries={excludeColumnHasActiveEntries}
            />
            <TableBody
              rows={rows}
              visibleColumnIds={visibleColumnIds}
              loading={loading}
              totalRowsCount={totalRowsCount}
              isSelected={isSelected}
              onToggleRow={onToggleRow}
              onCellContextMenu={onCellContextMenu}
              renderCell={renderCell}
              onRowDoubleClick={onRowDoubleClick}
            />
          </table>
        </div>
      </div>

      <TableFooter rowsLength={rows.length} totalRowsCount={totalRowsCount} />

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
                      <input type="number" className="dialog-cols__width-input" min={4} max={480} step={1} placeholder="авто" value={viewDraftColumnWidth(id)} onChange={(ev) => onViewDraftColumnWidthChange(id, ev.target.value)} aria-label={`Ширина колонки «${columnLabel(id)}», пиксели; пусто — по умолчанию`} />
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

export const ListTableShell = memo(ListTableShellInner) as typeof ListTableShellInner
