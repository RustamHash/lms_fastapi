import type { ReactNode } from 'react'

export type ColumnType = 'text' | 'number' | 'date' | 'datetime' | 'bool' | 'select'

export type ColumnConfig = {
  id: string
  label: string
  type: ColumnType
  sortable?: boolean
  filterable?: boolean
  options?: { value: string; label: string }[]
}

export type FilterType = 'text' | 'date' | 'select'

export type FilterConfig = {
  id: string
  type: FilterType
  label?: string
  options?: { value: string; label: string }[]
}

export type ToolbarConfig = {
  createHref?: string
  canCreate?: boolean
  showExport?: boolean
}

export type GroupActionsContext<Row> = {
  selectedIds: number[]
  selectedRows: Row[]
  reload: () => void
}

export type ColumnOverride<Row> = {
  href?: (row: Row) => string
  render?: (row: Row) => ReactNode
  label?: string
}

export type ListPageConfig<Row extends { id: number }> = {
  entityKey: string
  title: string
  subtitle?: string
  apiUrl: string
  
  columns: ColumnConfig[]
  filters?: FilterConfig[]
  toolbar?: ToolbarConfig
  groupActions?: (ctx: GroupActionsContext<Row>) => ReactNode
  columnOverrides?: Record<string, ColumnOverride<Row>>
}
