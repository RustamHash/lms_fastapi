import type { ReactNode, ComponentType } from 'react'

export type ColumnType = 'text' | 'number' | 'date' | 'bool' | 'select' | 'datetime'

export type ColumnConfig = {
  id: string
  label: string
  type: ColumnType
  sortable?: boolean
  filterable?: boolean
  options?: { value: string; label: string }[]
  width?: number
  hideByDefault?: boolean
}

export type FilterType = 'text' | 'date' | 'datetime' | 'select'

export type FilterConfig = {
  id: string
  type: FilterType
  label?: string
  options?: { value: string; label: string }[]
}

export type CreateFieldType = 'text' | 'number' | 'bool' | 'date' | 'password' | 'textarea'

export type CreateField = {
  key: string
  label: string
  type: CreateFieldType
  required?: boolean
}

export type ToolbarConfig = {
  createHref?: string
  /** Не предлагать «+», даже если есть listPath (логи, журнал). */
  disableCreate?: boolean
  canCreate?: boolean
  showExport?: boolean
  showRefresh?: boolean
  showColumnSettings?: boolean
  showResetFilters?: boolean
}

export type GroupActionContext<Row> = {
  selectedRows: Row[]
  selectedIds: number[]
  reload: () => void
  clearSelection: () => void
  notify: (message: string, kind: 'success' | 'error' | 'info' | 'warning') => void
}

export type GroupAction<Row> = {
  id: string
  label: string
  icon?: ReactNode
  confirmMessage?: string | ((rows: Row[]) => string)
  condition?: (rows: Row[]) => boolean
  disabled?: (rows: Row[]) => boolean
  maxSelection?: number
  executionMode?: 'sequential' | 'parallel'
  dialogComponent?: ComponentType<{
    rows: Row[]
    onComplete: (result: unknown) => void
    onCancel: () => void
  }>
  action: (rows: Row[], context: GroupActionContext<Row>) => Promise<void> | void
}

export type RowAction<Row> = {
  id: string
  label: string
  icon?: ReactNode
  href?: (row: Row) => string
  confirmMessage?: string | ((row: Row) => string)
  condition?: (row: Row) => boolean
  action?: (row: Row, context: GroupActionContext<Row>) => Promise<void> | void
}

export type ColumnOverride<Row> = {
  href?: (row: Row) => string
  render?: (row: Row) => ReactNode
  label?: string
  width?: number
}

export type EntityTab<T> = {
  id: string
  label: string
  icon?: ReactNode
  component: ComponentType<{
    entity: T
    onUpdate: (patch: Partial<T>) => Promise<void>
    reload: () => void
    notify: (message: string, kind: 'success' | 'error' | 'info' | 'warning') => void
  }>
  condition?: (entity: T) => boolean
}

export type ListPageConfig<Row extends { id: number }> = {
  entityKey: string
  title: string
  subtitle?: string
  apiUrl: string
  /** SPA-путь списка. Деталка: `{listPath}/{id}`, создание: `{listPath}/new`. */
  listPath?: string
  createFields?: CreateField[]
  /** POST, если отличается от apiUrl (список `/list`, остаток `/stock/add`). */
  createApiUrl?: string
  staleTime?: number
  
  columns?: ColumnConfig[]
  filters?: FilterConfig[]
  toolbar?: ToolbarConfig
  groupActions?: GroupAction<Row>[]
  rowActions?: RowAction<Row>[]
  columnOverrides?: Record<string, ColumnOverride<Row>>
  defaultSort?: { column: string; direction: 'asc' | 'desc' }
  toolbarComponents?: ReactNode[]
}

export type EntitySection<T> = {
  id: string
  title: string
  icon?: ReactNode
  fields: {
    key: keyof T
    label: string
    type?: 'text' | 'number' | 'date' | 'boolean' | 'link' | 'code'
    editable?: boolean
    required?: boolean
    format?: (value: unknown) => string
    href?: (row: T) => string
  }[]
}

export type EntityDetailConfig<T extends { id: number }> = {
  entityKey: string
  title: string
  apiUrl: string
  backUrl: string
  backLabel?: string
  
  sections?: EntitySection<T>[]
  tabs?: EntityTab<T>[]
  
  actions?: {
    edit?: boolean
    delete?: boolean
    custom?: {
      id: string
      label: string
      action: (entity: T, context: { reload: () => void; notify: (message: string, kind: 'success' | 'warning' | 'error' | 'info') => void }) => void
      condition?: (entity: T) => boolean
      confirmMessage?: string
    }[]
  }
  
  editForm?: ComponentType<{
    entity: T
    onSave: (patch: Partial<T>) => Promise<void>
    onCancel: () => void
  }>
}

export type EntityConfig<T extends { id: number }> = {
  list: ListPageConfig<T>
  detail?: EntityDetailConfig<T>
}
