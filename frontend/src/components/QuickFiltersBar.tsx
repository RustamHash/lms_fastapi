import { memo } from 'react'

type Props = {
  quickFilters: string[]
  filters: Record<string, string>
  columnFilters: Record<string, { kind: 'text' | 'select' | 'datetime' } & { options?: { value: string; label: string }[] }>
  columnLabel: (cid: string) => string
  onFilterChange: (cid: string, next: string) => void
}

function QuickFiltersBarInner({
  quickFilters,
  filters,
  columnFilters,
  columnLabel,
  onFilterChange,
}: Props) {
  if (quickFilters.length === 0) return null

  return (
    <div className="quick-filters-bar">
      {quickFilters.map((cid) => {
        const def = columnFilters[cid]
        if (!def) return null
        
        const label = columnLabel(cid)
        const value = filters[cid] ?? ''
        
        if (def.kind === 'select') {
          return (
            <label key={cid} className="quick-filter-item">
              <span className="quick-filter-item__label">{label}</span>
              <select
                className="quick-filter-item__select"
                value={value}
                onChange={(e) => onFilterChange(cid, e.target.value)}
              >
                <option value="">Все</option>
                {(def.options ?? []).map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </label>
          )
        }
        
        return (
          <label key={cid} className="quick-filter-item">
            <span className="quick-filter-item__label">{label}</span>
            <input
              type="text"
              className="quick-filter-item__input"
              value={value}
              onChange={(e) => onFilterChange(cid, e.target.value)}
              placeholder="Введите..."
            />
          </label>
        )
      })}
    </div>
  )
}

export const QuickFiltersBar = memo(QuickFiltersBarInner)
