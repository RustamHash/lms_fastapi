import { memo } from 'react'
import { ListFilterCell } from '../ListFilterCell'
import type { ColumnFilterDef } from '../ListTableShell'

type Props = {
  visibleColumnIds: string[]
  columnFilters: Record<string, ColumnFilterDef>
  filters: Record<string, string>
  excludeFilters: Record<string, string[]>
  onFilterChange: (cid: string, next: string) => void
  columnLabel: (cid: string) => string
  excludeColumnHasActiveEntries: (entries: string[] | undefined, def: ColumnFilterDef) => boolean
}

function TableFilterRowInner({
  visibleColumnIds,
  columnFilters,
  filters,
  excludeFilters,
  onFilterChange,
  columnLabel,
  excludeColumnHasActiveEntries,
}: Props) {
  return (
    <thead>
      <tr className="list-filter-row">
        <th />
        {visibleColumnIds.map((cid) => {
          const def = columnFilters[cid]
          const exList = excludeFilters[cid] ?? []
          const highlightExclude = excludeColumnHasActiveEntries(exList, def)
          return (
            <th key={`f-${cid}`}>
              <ListFilterCell
                kind={def.kind === 'select' ? 'select' : def.kind === 'datetime' ? 'datetime' : 'text'}
                value={filters[cid] ?? ''}
                onChange={(next) => onFilterChange(cid, next)}
                options={def.kind === 'select' ? def.options : undefined}
                aria-label={`Фильтр: ${columnLabel(cid)}`}
                highlightActive={highlightExclude}
              />
            </th>
          )
        })}
      </tr>
    </thead>
  )
}

export const TableFilterRow = memo(TableFilterRowInner)
