import { useCallback, useMemo, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { apiFetch } from '../../../lib/http'
import { useColumnPrefs } from '../../../hooks/useColumnPrefs'
import { useTableSettings, type TablePrefs } from '../../../hooks/useTableSettings'
import { useListPresets } from '../../../hooks/useListPresets'
import type { ListPageConfig, ColumnConfig } from '../types'

type SortState = {
  col: string | null
  dir: 'asc' | 'desc'
}

export function useEntityList<Row extends { id: number }>(config: ListPageConfig<Row>) {
  const queryClient = useQueryClient()
  
  const { data: rows = [], isLoading, error } = useQuery({
    queryKey: ['entity-system', config.entityKey],
    queryFn: async () => {
      const res = await apiFetch(config.apiUrl)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      return res.json() as Promise<Row[]>
    },
    staleTime: config.staleTime ?? 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  })
  
  const columnDefs = useMemo(
    () => config.columns.map((c) => ({ id: c.id, label: c.label })),
    [config.columns],
  )
  
  const defaultHidden = useMemo(
    () => config.columns.filter((c) => c.hideByDefault).map((c) => c.id),
    [config.columns],
  )
  
  const prefs = useColumnPrefs(config.entityKey, columnDefs, defaultHidden)
  
  const tableSettings = useTableSettings(config.entityKey)
  const listPresets = useListPresets(config.entityKey)
  
  const [sort, setSort] = useState<SortState>(
    tableSettings.prefs?.sort
      ? { col: tableSettings.prefs.sort.column, dir: tableSettings.prefs.sort.direction }
      : config.defaultSort
        ? { col: config.defaultSort.column, dir: config.defaultSort.direction }
        : { col: null, dir: 'asc' }
  )
  const [filters, setFilters] = useState<Record<string, string>>(
    tableSettings.prefs?.filters ?? {}
  )
  const [excludeFilters, setExcludeFilters] = useState<Record<string, string[]>>(
    tableSettings.prefs?.exclude_filters ?? {}
  )
  const [quickFilters, setQuickFilters] = useState<string[]>(
    tableSettings.prefs?.quick_filters ?? []
  )
  const [selected, setSelected] = useState<Set<number>>(() => new Set())
  
  // Автосохранение настроек при изменении
  const currentPrefs: TablePrefs = {
    order: prefs.order,
    hidden: prefs.hidden,
    widths: prefs.widths,
    filters,
    exclude_filters: excludeFilters,
    sort: sort.col ? { column: sort.col, direction: sort.dir } : null,
    quick_filters: quickFilters,
  }

  const saveCurrentPrefs = useCallback(() => {
    void tableSettings.save(currentPrefs)
  }, [currentPrefs, tableSettings])

  const resetToDefaults = useCallback(async () => {
    const defaults = await tableSettings.resetToDefaults()
    setFilters(defaults.filters)
    setExcludeFilters(defaults.exclude_filters)
    setSort(defaults.sort ? { col: defaults.sort.column, dir: defaults.sort.direction } : { col: null, dir: 'asc' })
    setQuickFilters(defaults.quick_filters)
  }, [tableSettings])

  const filtered = useMemo(() => {
    let result = [...rows]
    
    for (const [colId, raw] of Object.entries(filters)) {
      if (!raw || raw === '') continue
      const column = config.columns.find((c) => c.id === colId)
      if (!column) continue
      
      result = result.filter((row) => {
        const rowRecord = row as unknown as Record<string, unknown>
        return filterValue(rowRecord, column, raw)
      })
    }
    
    for (const [colId, values] of Object.entries(excludeFilters)) {
      const column = config.columns.find((c) => c.id === colId)
      if (!column) continue
      
      for (const exc of values) {
        if (!exc || exc === '') continue
        result = result.filter((row) => {
          const rowRecord = row as unknown as Record<string, unknown>
          return !filterValue(rowRecord, column, exc)
        })
      }
    }
    
    if (sort.col) {
      const column = config.columns.find((c) => c.id === sort.col)
      if (column) {
        const mul = sort.dir === 'asc' ? 1 : -1
        result.sort((a, b) => {
          const av = (a as unknown as Record<string, unknown>)[sort.col!]
          const bv = (b as unknown as Record<string, unknown>)[sort.col!]
          return mul * compareValues(av, bv, column.type)
        })
      }
    }
    
    return result
  }, [rows, filters, excludeFilters, sort, config.columns])
  
  const selectedCount = selected.size
  const allSelected = filtered.length > 0 && filtered.every((row) => selected.has(row.id))
  
  const toggleAll = useCallback((checked: boolean) => {
    if (checked) {
      setSelected(new Set(filtered.map((row) => row.id)))
    } else {
      setSelected(new Set())
    }
  }, [filtered])
  
  const toggleRow = useCallback((id: number, checked: boolean) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (checked) next.add(id)
      else next.delete(id)
      return next
    })
  }, [])
  
  const clearSelection = useCallback(() => {
    setSelected(new Set())
  }, [])
  
  const reload = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['entity-system', config.entityKey] })
    clearSelection()
  }, [queryClient, config.entityKey, clearSelection])
  
  const onSortHeaderClick = useCallback((colId: string) => {
    setSort((prev) => {
      if (prev.col !== colId) return { col: colId, dir: 'asc' }
      return { col: colId, dir: prev.dir === 'asc' ? 'desc' : 'asc' }
    })
  }, [])
  
  const resetFilters = useCallback(() => {
    setFilters({})
    setExcludeFilters({})
  }, [])
  
  const cellText = useCallback(
    (row: Row, colId: string): string => {
      const column = config.columns.find((c) => c.id === colId)
      if (!column) return ''
      return formatCellValue(row as unknown as Record<string, unknown>, column)
    },
    [config.columns],
  )
  
  const renderCell = useCallback(
    (row: Row, colId: string): React.ReactNode => {
      const override = config.columnOverrides?.[colId]
      if (override?.render) {
        return override.render(row)
      }
      if (override?.href) {
        return <a href={override.href(row)}>{cellText(row, colId)}</a>
      }
      return cellText(row, colId)
    },
    [config.columnOverrides, cellText],
  )
  
  const hasActiveFilters = useMemo(() => {
    const f = Object.values(filters).some((v) => v !== '')
    const x = Object.values(excludeFilters).some((arr) => arr.some((v) => v !== ''))
    return f || x
  }, [filters, excludeFilters])
  
  return {
    rows: filtered,
    totalRowsCount: rows.length,
    loading: isLoading,
    error: error ? String(error) : null,
    sortCol: sort.col,
    sortDir: sort.dir,
    onSortHeaderClick,
    filters,
    setFilters,
    excludeFilters,
    setExcludeFilters,
    resetFilters,
    hasActiveFilters,
    selected,
    selectedCount,
    allSelected,
    toggleAll,
    toggleRow,
    clearSelection,
    prefs,
    cellText,
    renderCell,
    reload,
    
    // настройки таблицы и пресеты
    tableSettings,
    listPresets,
    quickFilters,
    setQuickFilters,
    saveCurrentPrefs,
    resetToDefaults,
  }
}

function formatCellValue(row: Record<string, unknown>, column: ColumnConfig): string {
  const value = row[column.id]
  if (value == null) return '—'
  
  switch (column.type) {
    case 'date':
    case 'datetime':
      return formatDt(String(value))
    case 'bool':
      return value ? 'Да' : 'Нет'
    case 'select': {
      const opt = column.options?.find((o) => o.value === String(value))
      return opt?.label ?? String(value)
    }
    default:
      return String(value)
  }
}

function compareValues(a: unknown, b: unknown, type: string): number {
  if (a == null && b == null) return 0
  if (a == null) return 1
  if (b == null) return -1
  
  switch (type) {
    case 'number':
      return Number(a) - Number(b)
    case 'date':
    case 'datetime':
      return new Date(String(a)).getTime() - new Date(String(b)).getTime()
    case 'bool':
      return Number(a) - Number(b)
    default:
      return String(a).localeCompare(String(b), 'ru', { sensitivity: 'base' })
  }
}

function filterValue(row: Record<string, unknown>, column: ColumnConfig, raw: string): boolean {
  const value = formatCellValue(row, column)
  
  if (raw === '') return true
  if (column.type === 'bool' || column.type === 'select') {
    const actual = column.type === 'bool' ? String(Boolean(row[column.id])) : String(row[column.id] ?? '')
    return actual === raw
  }
  
  return value.toLowerCase().includes(raw.toLowerCase())
}

function formatDt(iso: string): string {
  if (!iso) return '—'
  try {
    const d = new Date(iso)
    if (Number.isNaN(d.getTime())) return iso
    const p = (n: number) => String(n).padStart(2, '0')
    return `${p(d.getDate())}.${p(d.getMonth() + 1)}.${d.getFullYear()} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
  } catch {
    return iso
  }
}
