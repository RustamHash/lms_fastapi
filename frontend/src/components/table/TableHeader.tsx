import { memo, type PointerEvent as ReactPointerEvent, type MouseEvent as ReactMouseEvent } from 'react'
import { LIST_COL_WIDTH_DEFAULT } from '../../features/lists/columnWidthConstants'

type Props = {
  visibleColumnIds: string[]
  columnLabel: (cid: string) => string
  sortCol: string | null
  sortDir: 'asc' | 'desc'
  onSortHeaderClick: (cid: string) => void
  columnWidthsPx: Record<string, number>
  onColResizePointerDown: (cid: string, e: ReactPointerEvent<HTMLSpanElement>) => void
  onColResizeDoubleClick: (cid: string, e: ReactMouseEvent) => void
  dragColPreview: { colId: string; widthPx: number } | null
  colDragRef: React.MutableRefObject<{ colId: string; startX: number; startW: number; lastW: number } | null>
}

function TableHeaderInner({
  visibleColumnIds,
  columnLabel,
  sortCol,
  sortDir,
  onSortHeaderClick,
  columnWidthsPx,
  onColResizePointerDown,
  onColResizeDoubleClick,
  dragColPreview,
}: Props) {
  function colWidthPx(cid: string): number {
    if (dragColPreview?.colId === cid) return dragColPreview.widthPx
    return columnWidthsPx[cid] ?? LIST_COL_WIDTH_DEFAULT
  }

  return (
    <>
      <colgroup>
        <col className="list-table__col-cb" />
        {visibleColumnIds.map((cid) => (
          <col key={cid} style={{ width: `${colWidthPx(cid)}px` }} />
        ))}
      </colgroup>
      <thead>
        <tr className="list-table__head-row">
          <th className="list-table__cb">
            <input type="checkbox" aria-label="Выбрать все на странице" />
          </th>
          {visibleColumnIds.map((cid) => {
            const label = columnLabel(cid)
            const active = sortCol === cid
            const ariaSort = active ? (sortDir === 'asc' ? 'ascending' : 'descending') : 'none'
            return (
              <th key={cid} aria-sort={ariaSort} className="list-table__th-col">
                <button
                  type="button"
                  className="list-table__sort-btn"
                  onClick={() => onSortHeaderClick(cid)}
                  title={active ? (sortDir === 'asc' ? 'По убыванию' : 'По возрастанию') : 'Сортировать'}
                >
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
      </thead>
    </>
  )
}

export const TableHeader = memo(TableHeaderInner)
