/**
 * Типы метаданных полей сущностей.
 * Формат соответствует GET /api/v1/entities/{entity}/fields
 */

export type FieldType =
  | 'integer'
  | 'string'
  | 'boolean'
  | 'date'
  | 'datetime'
  | 'money'
  | 'enum'
  | 'select'
  | 'object'

export type FieldMeta = {
  title: string
  type: FieldType
  required?: boolean
  readonly?: boolean
  /** Для enum: список вариантов */
  enum?: { value: string; label: string }[]
  /** Для select: источник опций */
  endpoint?: string
  label_field?: string
  value_field?: string
  /** Для money */
  currency?: string
  /** Для date/datetime */
  format?: string
  /** Для object: вложенные поля */
  nested?: Record<string, FieldMeta>
}

export type EntityFieldsResponse = {
  entity: string
  fields: Record<string, FieldMeta>
}

/** Плоское поле для таблицы */
export type FlatField = {
  /** Путь: 'legal_entity.name' */
  path: string
  title: string
  type: FieldType
  readonly?: boolean
  /** Глубина: 0 — верхний уровень */
  depth: number
  /** Родительский путь: 'legal_entity' */
  parent?: string
}
