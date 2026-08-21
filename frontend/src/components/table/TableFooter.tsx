import { memo } from 'react'

type Props = {
  rowsLength: number
  totalRowsCount: number
}

function TableFooterInner({ rowsLength, totalRowsCount }: Props) {
  return (
    <div className="list-table-footer" aria-live="polite">
      <span className="list-table-count">
        Показано {rowsLength} из {totalRowsCount}
      </span>
    </div>
  )
}

export const TableFooter = memo(TableFooterInner)
