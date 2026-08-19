import { formatDt } from '../../lib/formatDt'
import type { ColumnConfig, ColumnType } from './types'

export function formatCellValue(row: Record<string, unknown>, column: ColumnConfig): string {
  const value = row[column.id]
  
  if (value == null) return '—'
  
  switch (column.type) {
    case 'number':
      return String(value)
    case 'date':
      return formatDt(String(value))
    case 'bool':
      return value ? 'Да' : 'Нет'
    case 'select': {
      const opt = column.options?.find((o) => o.value === String(value))
      return opt?.label ?? String(value)
    }
    case 'text':
    default:
      return String(value)
  }
}

export function compareValues(a: unknown, b: unknown, type: ColumnType): number {
  if (a == null && b == null) return 0
  if (a == null) return 1
  if (b == null) return -1
  
  switch (type) {
    case 'number':
      return Number(a) - Number(b)
    case 'date':
      return new Date(String(a)).getTime() - new Date(String(b)).getTime()
    case 'bool':
      return Number(a) - Number(b)
    case 'select':
    case 'text':
    default:
      return String(a).localeCompare(String(b), 'ru', { sensitivity: 'base' })
  }
}

export function filterValue(row: Record<string, unknown>, column: ColumnConfig, raw: string): boolean {
  const value = formatCellValue(row, column)
  
  if (raw === '') return true
  if (column.type === 'bool' || column.type === 'select') {
    const actual = column.type === 'bool' ? String(Boolean(row[column.id])) : String(row[column.id] ?? '')
    return actual === raw
  }
  
  return value.toLowerCase().includes(raw.toLowerCase())
}
