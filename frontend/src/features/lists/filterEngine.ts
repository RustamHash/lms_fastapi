import type { DateTimeFilterState, NumberFilterState, TextFilterState } from './filterTypes'

/** Парсинг числа из строки фильтра (запятая/точка). */
export function parseFilterNumber(raw: string): number | null {
  const t = raw.trim().replace(',', '.')
  if (t === '') return null
  const n = Number(t)
  return Number.isFinite(n) ? n : null
}

/** Миллисекунды из ISO или null. */
export function parseIsoToMs(iso: string | null | undefined): number | null {
  if (iso == null || iso === '') return null
  const ms = Date.parse(iso)
  return Number.isNaN(ms) ? null : ms
}

/** Дата без времени из фильтра → полночь локального дня (как в datetime-local). */
export function normalizeFilterDateTimeLocal(raw: string): string {
  const t = raw.trim()
  if (!t) return ''
  if (/^\d{4}-\d{2}-\d{2}$/.test(t)) return `${t}T00:00`
  if (/^\d{4}-\d{2}-\d{2}T$/.test(t)) return `${t}00:00`
  return t
}

/** Парсинг даты из строки фильтра (input type=date / datetime-local или ISO). */
export function parseFilterDateMs(raw: string | undefined): number | null {
  if (raw == null || raw.trim() === '') return null
  const ms = Date.parse(normalizeFilterDateTimeLocal(raw.trim()))
  return Number.isNaN(ms) ? null : ms
}

/** Последняя миллисекунда локального календарного дня для момента startOfDayMs. */
export function endOfLocalDayMs(startOfDayMs: number): number {
  const d = new Date(startOfDayMs)
  d.setHours(23, 59, 59, 999)
  return d.getTime()
}

function isLocalMidnight(ms: number): boolean {
  const d = new Date(ms)
  return (
    d.getHours() === 0 &&
    d.getMinutes() === 0 &&
    d.getSeconds() === 0 &&
    d.getMilliseconds() === 0
  )
}

/**
 * Если raw совпадает с sentinel — вернуть, пустое ли поле даты в строке.
 * Иначе undefined (смотреть обычное сопоставление).
 */
export function matchDateEmptySentinel(
  iso: string | null,
  raw: string,
  sentinel: string,
): boolean | undefined {
  if (raw !== sentinel) return undefined
  return iso == null
}

/** Select по bool в стиле текущего UI: '', 'true', 'false'. */
export function matchBoolSelect(isActive: boolean, raw: string): boolean {
  if (raw === 'true') return isActive
  if (raw === 'false') return !isActive
  return true
}

/** Подстрока в ID как сейчас: без перевода регистра. */
export function matchIdSubstring(id: number, needleRaw: string): boolean {
  const t = needleRaw.trim()
  if (t === '') return true
  return String(id).includes(t)
}

/** Текстовые операторы (покрытие будущего UI; сейчас можно передавать только contains). */
export function matchTextFilter(haystack: string, state: TextFilterState): boolean {
  const needle = state.value.trim()
  if (needle === '') return true
  const hc = haystack.toLowerCase()
  const nc = needle.toLowerCase()
  switch (state.op) {
    case 'contains':
      return hc.includes(nc)
    case 'not_contains':
      return !hc.includes(nc)
    case 'equals':
      return haystack === needle
    case 'starts_with':
      return hc.startsWith(nc)
    case 'ends_with':
      return hc.endsWith(nc)
    default:
      return hc.includes(nc)
  }
}

/** Как сейчас для code/name: регистронезависимое «содержит». */
export function matchLegacyTextContains(haystack: string, needleRaw: string): boolean {
  return matchTextFilter(haystack, { op: 'contains', value: needleRaw })
}

/**
 * Как сейчас для колонок даты: поиск по подстроке в ISO и в отформатированном отображении.
 */
export function matchLegacyDateTimeSubstring(
  iso: string | null,
  needleRaw: string,
  formattedDisplay: string,
): boolean {
  const t = needleRaw.trim()
  if (t === '') return true
  const low = t.toLowerCase()
  const r = (iso ?? '').toLowerCase()
  const d = formattedDisplay.toLowerCase()
  return r.includes(low) || d.includes(low)
}

/** Числовое сравнение по состоянию фильтра (для заказов и т.д.). */
export function matchNumberFilter(value: number | null, state: NumberFilterState): boolean {
  const v = value
  const a = parseFilterNumber(state.value)
  const b = state.valueTo != null && state.valueTo !== '' ? parseFilterNumber(state.valueTo) : null

  if (state.op === 'between') {
    if (v == null || Number.isNaN(v)) return false
    if (a == null || b == null) return true
    const lo = Math.min(a, b)
    const hi = Math.max(a, b)
    return v >= lo && v <= hi
  }

  if (v == null || Number.isNaN(v)) return false
  if (a == null) return true

  switch (state.op) {
    case 'eq':
      return v === a
    case 'ne':
      return v !== a
    case 'gt':
      return a != null && v > a
    case 'gte':
      return a != null && v >= a
    case 'lt':
      return a != null && v < a
    case 'lte':
      return a != null && v <= a
    default:
      return true
  }
}

/** Дата/время по полному состоянию (будущий UI). Legacy-подстрока — отдельно. */
export function matchDateTimeFilter(
  iso: string | null,
  state: DateTimeFilterState,
  localeDisplay: string,
): boolean {
  const ms = parseIsoToMs(iso)

  switch (state.op) {
    case 'is_empty':
      return iso == null || iso === ''
    case 'is_not_empty':
      return iso != null && iso !== ''
    case 'after': {
      const t = parseFilterDateMs(state.value)
      if (t == null) return false
      if (ms == null) return false
      return ms > t
    }
    case 'before': {
      const t = parseFilterDateMs(state.value)
      if (t == null) return false
      if (ms == null) return false
      return ms < t
    }
    case 'between': {
      const t1 = parseFilterDateMs(state.value)
      const t2 = parseFilterDateMs(state.valueTo)
      if (t1 == null || t2 == null) return false
      if (ms == null) return false
      const lo = Math.min(t1, t2)
      const hiStart = Math.max(t1, t2)
      const dateOnlyRange = isLocalMidnight(t1) && isLocalMidnight(t2)
      const hi = dateOnlyRange ? endOfLocalDayMs(hiStart) : hiStart
      return ms >= lo && ms <= hi
    }
    default:
      return matchLegacyDateTimeSubstring(iso, state.value ?? '', localeDisplay)
  }
}
