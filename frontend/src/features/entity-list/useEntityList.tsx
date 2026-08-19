import { useCallback, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { apiFetch } from '../../lib/http'
import { useColumnPrefs } from '../../hooks/useColumnPrefs'
import type { ListPageConfig } from './types'
import { compareValues, filterValue, formatCellValue } from './columnUtils'

type SortState = {
  col: string | null
  dir: 'asc' | 'desc'
}

export function useEntityList<Row extends { id: number }>(config: ListPageConfig<Row>) {
  const queryClient = useQueryClient()
  
  // Загрузка данных с кэшем
  const { data: rows = [], isLoading, error } = useQuery({
    queryKey: ['entity-list', config.entityKey],
    queryFn: async () => {
      const res = await apiFetch(config.apiUrl)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      return res.json() as Promise<Row[]>
    },
    staleTime: 5 * 60 * 1000, // 5 минут
    refetchOnWindowFocus: false,
  })
  
  // Настройки колонок
  const columnDefs = useMemo(
    () => config.columns.map((c) => ({ id: c.id, label: c.label })),
    [config.columns],
  )
  
  const defaultHidden = useMemo(
    () => config.columns.filter((c) => c.type === 'date' || c.id.endsWith('_by_id')).map((c) => c.id),
    [config.columns],
  )
  
  const prefs = useColumnPrefs(config.entityKey, columnDefs, defaultHidden)
  
  // Состояние списка
  const [sort, setSort] = useState<SortState>({ col: null, dir: 'asc' })
  const [filters, setFilters] = useState<Record<string, string>>({})
  const [excludeFilters, setExcludeFilters] = useState<Record<string, string[]>>({})
  const [selected, setSelected] = useState<Set<number>>(() => new Set())
  
  // Обработка данных
  const filtered = useMemo(() => {
    let result = [...rows]
    
    // Применяем фильтры
    for (const [colId, raw] of Object.entries(filters)) {
      if (!raw || raw === '') continue
      const column = config.columns.find((c) => c.id === colId)
      if (!column) continue
      
      result = result.filter((row) => {
        const rowRecord = row as unknown as Record<string, unknown>
        return filterValue(rowRecord, column, raw)
      })
    }
    
    // Применяем исключения
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
    
    // Применяем сортировку
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
  
  // Выбор
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
  
  // Reload
  const reload = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['entity-list', config.entityKey] })
    clearSelection()
  }, [queryClient, config.entityKey, clearSelection])
  
  // Сортировка
  const onSortHeaderClick = useCallback((colId: string) => {
    setSort((prev) => {
      if (prev.col !== colId) return { col: colId, dir: 'asc' }
      return { col: colId, dir: prev.dir === 'asc' ? 'desc' : 'asc' }
    })
  }, [])
  
  // Сброс фильтров
  const resetFilters = useCallback(() => {
    setFilters({})
    setExcludeFilters({})
  }, [])
  
  // Форматирование ячейки
  const cellText = useCallback(
    (row: Row, colId: string): string => {
      const column = config.columns.find((c) => c.id === colId)
      if (!column) return ''
      return formatCellValue(row as unknown as Record<string, unknown>, column)
    },
    [config.columns],
  )
  
  // Рендер ячейки с учётом override
  const renderCell = useCallback(
    (row: Row, colId: string): React.ReactNode => {
      const override = config.columnOverrides?.[colId]
      if (override?.render) {
        return override.render(row)
      }
      if (override?.href) {
        return <Link to={override.href(row)}>{cellText(row, colId)}</Link>
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
    // данные
    rows: filtered,
    totalRowsCount: rows.length,
    loading: isLoading,
    error: error ? String(error) : null,
    
    // сортировка
    sortCol: sort.col,
    sortDir: sort.dir,
    onSortHeaderClick,
    
    // фильтры
    filters,
    setFilters,
    excludeFilters,
    setExcludeFilters,
    resetFilters,
    hasActiveFilters,
    
    // выбор
    selected,
    selectedCount,
    allSelected,
    toggleAll,
    toggleRow,
    clearSelection,
    
    // prefs
    prefs,
    
    // утилиты
    cellText,
    renderCell,
    reload,
  }
}
