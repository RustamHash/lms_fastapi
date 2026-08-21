import { memo, useMemo } from 'react'
import type { TablePrefs } from '../hooks/useTableSettings'

type Props = {
  prefs: TablePrefs
  columnLabel: (columnId: string) => string
  onRemoveFilter: (columnId: string) => void
  onRemoveExclude: (columnId: string, value: string) => void
}

function ActiveFiltersBarInner({
  prefs,
  columnLabel,
  onRemoveFilter,
  onRemoveExclude,
}: Props) {
  const hasActiveFilters = useMemo(() => {
    const hasFilters = Object.values(prefs.filters).some(v => v !== '')
    const hasExcludes = Object.values(prefs.exclude_filters).some(arr => arr.length > 0)
    return hasFilters || hasExcludes
  }, [prefs.filters, prefs.exclude_filters])

  if (!hasActiveFilters && prefs.quick_filters.length === 0) return null

  return (
    <div className="active-filters-bar">
      <div className="active-filters-bar__chips">
        {Object.entries(prefs.filters).map(([columnId, value]) => {
          if (!value || value === '') return null
          return (
            <span key={`filter-${columnId}`} className="filter-chip">
              <span className="filter-chip__label">{columnLabel(columnId)}:</span>
              <span className="filter-chip__value">{value}</span>
              <button
                type="button"
                className="filter-chip__remove"
                onClick={() => onRemoveFilter(columnId)}
                aria-label={`Убрать фильтр ${columnLabel(columnId)}`}
                title="Убрать фильтр"
              >
                ×
              </button>
            </span>
          )
        })}
        
        {Object.entries(prefs.exclude_filters).map(([columnId, values]) => {
          return values.map((value, index) => (
            <span key={`exclude-${columnId}-${index}`} className="filter-chip filter-chip--exclude">
              <span className="filter-chip__label">НЕ {columnLabel(columnId)}:</span>
              <span className="filter-chip__value">{value}</span>
              <button
                type="button"
                className="filter-chip__remove"
                onClick={() => onRemoveExclude(columnId, value)}
                aria-label={`Убрать исключение ${columnLabel(columnId)}`}
                title="Убрать исключение"
              >
                ×
              </button>
            </span>
          ))
        })}
      </div>


    </div>
  )
}


export const ActiveFiltersBar = memo(ActiveFiltersBarInner)
