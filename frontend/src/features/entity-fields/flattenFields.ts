import type { FieldMeta, FlatField } from './types'


/**
 * Рекурсивно разворачивает дерево полей в плоский список.
 */
export function flattenFields(
  fields: Record<string, FieldMeta>,
  parentPath = '',
  depth = 0,
  parentTitle = '',
): FlatField[] {
  const result: FlatField[] = []

  for (const [key, meta] of Object.entries(fields)) {
    const path = parentPath ? `${parentPath}.${key}` : key
    const title = parentTitle ? `${parentTitle} → ${meta.title}` : meta.title

    result.push({
      path,
      title,
      type: meta.type === 'datetime' ? 'datetime' : meta.type,
      readonly: meta.readonly,
      depth,
      parent: parentPath || undefined,
    })

    if (meta.type === 'object' && meta.nested) {
      result.push(...flattenFields(meta.nested, path, depth + 1, title))
    }
  }

  return result
}

/**
 * Возвращает все примитивные поля (не object), которые можно отображать в таблице.
 */
export function getDisplayableFields(fields: Record<string, FieldMeta>): FlatField[] {
  return flattenFields(fields).filter((f) => f.type !== 'object')
}

/**
 * Возвращает поля по умолчанию: верхний уровень + первый уровень вложенных.
 */
export function getDefaultFields(fields: Record<string, FieldMeta>): FlatField[] {
  const all = getDisplayableFields(fields)
  return all.filter((f) => f.depth <= 1)
}
