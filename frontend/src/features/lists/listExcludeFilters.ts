import { isDateTimeFilterActive } from './dateTimeFilterCodec'

type ColFilterKind = 'text' | 'datetime' | 'select'

/** Есть ли по колонке хотя бы одно «живое» значение в списке исключений. */
export function excludeColumnHasActiveEntries(
  entries: string[] | undefined,
  def: { kind: ColFilterKind },
): boolean {
  const list = entries ?? []
  if (list.length === 0) return false
  if (def.kind === 'datetime') return list.some((s) => isDateTimeFilterActive(s))
  if (def.kind === 'select') return list.some((s) => s !== '')
  return list.some((s) => s.trim() !== '')
}
