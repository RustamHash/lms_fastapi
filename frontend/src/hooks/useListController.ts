import { useCallback, useMemo, useState, type MouseEvent } from 'react'

type SortState<ColId extends string> = {
  col: ColId | null
  dir: 'asc' | 'desc'
}

type CtxMenuState<Row, ColId extends string> = {
  x: number
  y: number
  row: Row
  colId: ColId
}

type Params<Row extends { id: number }, ColId extends string> = {
  rows: Row[]
  matchRow: (row: Row, filters: Record<string, string>, excludeFilters: Record<string, string[]>) => boolean
  compareRows: (a: Row, b: Row, col: ColId) => number
  filterValueFromRow: (row: Row, col: ColId) => string
  clampMenuPosition: (x: number, y: number) => { x: number; y: number }
}

export function useListController<Row extends { id: number }, ColId extends string>({
  rows,
  matchRow,
  compareRows,
  filterValueFromRow,
  clampMenuPosition,
}: Params<Row, ColId>) {
  const [filters, setFilters] = useState<Record<string, string>>({})
  const [excludeFilters, setExcludeFilters] = useState<Record<string, string[]>>({})
  const [sort, setSort] = useState<SortState<ColId>>({ col: null, dir: 'asc' })
  const [selected, setSelected] = useState<Set<number>>(() => new Set())
  const [ctxMenu, setCtxMenu] = useState<CtxMenuState<Row, ColId> | null>(null)

  const filtered = useMemo(
    () => rows.filter((row) => matchRow(row, filters, excludeFilters)),
    [rows, filters, excludeFilters, matchRow],
  )

  const sortedFiltered = useMemo(() => {
    const col = sort.col
    if (!col) return filtered
    const mul = sort.dir === 'asc' ? 1 : -1
    return [...filtered].sort((a, b) => mul * compareRows(a, b, col))
  }, [filtered, sort, compareRows])

  const selectedCount = selected.size
  const allSelected =
    sortedFiltered.length > 0 && sortedFiltered.every((row) => selected.has(row.id))

  const onSortHeaderClick = useCallback((cid: ColId) => {
    setSort((s) => {
      if (s.col !== cid) return { col: cid, dir: 'asc' }
      return { col: cid, dir: s.dir === 'asc' ? 'desc' : 'asc' }
    })
  }, [])

  const resetFilters = useCallback(() => {
    setFilters({})
    setExcludeFilters({})
  }, [])

  const clearSelection = useCallback(() => {
    setSelected(new Set())
  }, [])

  const onCellContextMenu = useCallback(
    (e: MouseEvent<HTMLTableCellElement>, row: Row, colId: ColId) => {
      e.preventDefault()
      const { x, y } = clampMenuPosition(e.clientX, e.clientY)
      setCtxMenu({ x, y, row, colId })
    },
    [clampMenuPosition],
  )

  const applyFilterByCellValue = useCallback(() => {
    setCtxMenu((m) => {
      if (!m) return null
      const v = filterValueFromRow(m.row, m.colId)
      setFilters((prev) => ({ ...prev, [m.colId]: v }))
      return null
    })
  }, [filterValueFromRow])

  const applyExcludeCellValue = useCallback(() => {
    setCtxMenu((m) => {
      if (!m) return null
      const v = filterValueFromRow(m.row, m.colId)
      setExcludeFilters((prev) => {
        const cur = prev[m.colId] ?? []
        if (cur.includes(v)) return prev
        return { ...prev, [m.colId]: [...cur, v] }
      })
      return null
    })
  }, [filterValueFromRow])

  const closeCtxMenu = useCallback(() => setCtxMenu(null), [])

  const toggleAll = useCallback(
    (checked: boolean) => {
      if (checked) {
        setSelected(new Set(sortedFiltered.map((row) => row.id)))
      } else {
        setSelected(new Set())
      }
    },
    [sortedFiltered],
  )

  const toggleRow = useCallback((id: number, checked: boolean) => {
    setSelected((prev) => {
      const n = new Set(prev)
      if (checked) n.add(id)
      else n.delete(id)
      return n
    })
  }, [])

  return {
    filters,
    setFilters,
    excludeFilters,
    setExcludeFilters,
    sort,
    onSortHeaderClick,
    selected,
    selectedCount,
    allSelected,
    toggleAll,
    toggleRow,
    filtered,
    sortedFiltered,
    resetFilters,
    clearSelection,
    ctxMenu,
    setCtxMenu,
    closeCtxMenu,
    onCellContextMenu,
    applyFilterByCellValue,
    applyExcludeCellValue,
  }
}
