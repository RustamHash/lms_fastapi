import { LIST_FILTER_EMPTY_DATE } from './filterTypes'
import { matchDateTimeFilter, matchLegacyDateTimeSubstring } from './filterEngine'

/** Версия сериализации в строке фильтра (хранится в Record<string, string>). */
export type DateTimeFilterPayloadV1 = {
  v: 1
  /** contains | after | before | between | empty | notEmpty */
  m: 'ct' | 'aft' | 'bef' | 'btw' | 'emp' | 'nem'
  /** подстрока для ct */
  t?: string
  /** datetime-local или ISO */
  a?: string
  b?: string
}

export function encodeDateTimeFilter(p: DateTimeFilterPayloadV1): string {
  return JSON.stringify(p)
}

/** Пустая строка → null. Не-JSON → режим «содержит» с этим текстом. */
export function decodeDateTimeFilter(raw: string): DateTimeFilterPayloadV1 | null {
  const s = raw.trim()
  if (s === '') return null
  if (s.startsWith('{')) {
    try {
      const o = JSON.parse(s) as DateTimeFilterPayloadV1
      if (o && o.v === 1 && typeof o.m === 'string') return o
    } catch {
      /* legacy */
    }
  }
  return { v: 1, m: 'ct', t: raw }
}

export function isDateTimeFilterActive(raw: string): boolean {
  if (raw.trim() === '') return false
  if (raw === LIST_FILTER_EMPTY_DATE) return true
  const d = decodeDateTimeFilter(raw)
  if (!d) return false
  switch (d.m) {
    case 'ct':
      return (d.t ?? '').trim() !== ''
    case 'aft':
    case 'bef':
      return (d.a ?? '').trim() !== ''
    case 'btw':
      return (d.a ?? '').trim() !== '' && (d.b ?? '').trim() !== ''
    case 'emp':
    case 'nem':
      return true
    default:
      return false
  }
}

export function dateTimeFilterHint(raw: string): string | null {
  if (raw === LIST_FILTER_EMPTY_DATE) return null
  const d = decodeDateTimeFilter(raw)
  if (!d) return null
  const ta = (d.a ?? '').slice(0, 16)
  const tb = (d.b ?? '').slice(0, 16)
  const tt = (d.t ?? '').slice(0, 20)
  switch (d.m) {
    case 'ct':
      return tt ? `содерж.: ${tt}${(d.t ?? '').length > 20 ? '…' : ''}` : null
    case 'aft':
      return `после ${ta || '…'}`
    case 'bef':
      return `до ${ta || '…'}`
    case 'btw':
      return `${ta || '…'}–${tb || '…'}`
    case 'emp':
      return 'пусто'
    case 'nem':
      return 'не пусто'
    default:
      return null
  }
}

/** Сопоставление ISO даты строки с фильтром из ячейки фильтра. */
export function matchDateTimeColumnFilter(
  iso: string | null,
  raw: string,
  formatDisplay: (iso: string | null) => string,
): boolean {
  const emptyOnly = raw === LIST_FILTER_EMPTY_DATE
  if (emptyOnly) return iso == null

  const d = decodeDateTimeFilter(raw)
  if (!d) return true

  switch (d.m) {
    case 'ct':
      return matchLegacyDateTimeSubstring(iso, d.t ?? '', formatDisplay(iso))
    case 'emp':
      return iso == null || iso === ''
    case 'nem':
      return iso != null && iso !== ''
    case 'aft':
      return matchDateTimeFilter(iso, { op: 'after', value: d.a }, formatDisplay(iso))
    case 'bef':
      return matchDateTimeFilter(iso, { op: 'before', value: d.a }, formatDisplay(iso))
    case 'btw':
      return matchDateTimeFilter(
        iso,
        { op: 'between', value: d.a, valueTo: d.b },
        formatDisplay(iso),
      )
    default:
      return true
  }
}

/** Для «фильтр по значению ячейки» по колонке даты. */
export function encodeDateTimeFilterFromCellValue(iso: string | null, formatDisplay: (iso: string | null) => string): string {
  if (iso == null || iso === '') {
    return LIST_FILTER_EMPTY_DATE
  }
  return encodeDateTimeFilter({ v: 1, m: 'ct', t: formatDisplay(iso) })
}
