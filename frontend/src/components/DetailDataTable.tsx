import type { ReactNode } from 'react'

export type DetailTableColumn<T> = {
  id: string
  label: string
  render: (row: T) => ReactNode
}

type Props<T> = {
  columns: DetailTableColumn<T>[]
  rows: T[]
  empty: string
  rowKey: (row: T, index: number) => string | number
  rowClassName?: (row: T) => string | undefined
}

export function DetailDataTable<T>({
  columns,
  rows,
  empty,
  rowKey,
  rowClassName,
}: Props<T>) {
  return (
    <div className="detail-data-table">
      <div className="table-wrap">
        <table className="list-table">
          <thead>
            <tr className="list-table__head-row">
              {columns.map((col) => (
                <th key={col.id}>{col.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td className="list-table__empty" colSpan={columns.length}>
                  {empty}
                </td>
              </tr>
            ) : (
              rows.map((row, index) => (
                <tr key={rowKey(row, index)} className={rowClassName?.(row)}>
                  {columns.map((col) => (
                    <td key={col.id}>{col.render(row)}</td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
