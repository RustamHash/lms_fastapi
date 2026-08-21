import { memo, type MouseEvent, type ReactNode } from 'react'

type Props<Row extends { id: number }> = {
  rows: Row[]
  visibleColumnIds: string[]
  loading: boolean
  totalRowsCount: number
  allSelected: boolean
  onToggleAll: (checked: boolean) => void
  isSelected: (id: number) => boolean
  onToggleRow: (id: number, checked: boolean) => void
  onCellContextMenu: (e: MouseEvent<HTMLTableCellElement>, row: Row, colId: string) => void
  renderCell: (row: Row, cid: string) => ReactNode
  onRowDoubleClick?: (row: Row) => void
}

function TableBodyInner<Row extends { id: number }>({
  rows,
  visibleColumnIds,
  loading,
  totalRowsCount,
  allSelected,
  onToggleAll,
  isSelected,
  onToggleRow,
  onCellContextMenu,
  renderCell,
  onRowDoubleClick,
}: Props<Row>) {
  return (
    <tbody>
      <tr className="list-table__header-row-spacer" aria-hidden>
        <td className="list-table__cb" style={{ padding: 0, border: 'none' }} />
      </tr>
      <tr>
        <td className="list-table__cb">
          <input type="checkbox" checked={allSelected} onChange={(e) => onToggleAll(e.target.checked)} aria-label="Выбрать все на странице" />
        </td>
      </tr>
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
          <td className="list-table__empty" colSpan={visibleColumnIds.length + 1} role="status">
            Нет данных по текущим фильтрам. Измените условия в строке фильтров или сбросьте их кнопкой на панели над таблицей.
          </td>
        </tr>
      ) : (
        rows.map((row) => (
          <tr key={row.id}>
            <td className="list-table__cb">
              <input type="checkbox" checked={isSelected(row.id)} onChange={(e) => onToggleRow(row.id, e.target.checked)} aria-label={`Выбрать строку ${row.id}`} />
            </td>
            {visibleColumnIds.map((cid) => (
              <td
                key={cid}
                onContextMenu={(e) => onCellContextMenu(e, row, cid)}
                onDoubleClick={(e) => {
                  e.preventDefault()
                  onRowDoubleClick?.(row)
                }}
              >
                {renderCell(row, cid)}
              </td>
            ))}
          </tr>
        ))
      )}
    </tbody>
  )
}

export const TableBody = memo(TableBodyInner) as typeof TableBodyInner
