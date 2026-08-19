/** Минимальная ширина колонки данных (px). */
export const LIST_COL_WIDTH_MIN = 4
/** Максимальная ширина колонки данных (px). */
export const LIST_COL_WIDTH_MAX = 480
/** Ширина по умолчанию, если в prefs нет записи (px). */
export const LIST_COL_WIDTH_DEFAULT = 112
/** При измерении подгонки не учитывать больше символов (одна «простыня» не раздует колонку). */
export const LIST_COL_MEASURE_MAX_CHARS = 80

export function clampListColumnWidthPx(w: number): number {
  if (!Number.isFinite(w)) return LIST_COL_WIDTH_DEFAULT
  return Math.min(LIST_COL_WIDTH_MAX, Math.max(LIST_COL_WIDTH_MIN, Math.round(w)))
}

/** Значения для полей «ширина, px» в диалоге «Вид» при открытии. */
export function columnWidthsDraftFromRecord(
  order: readonly string[],
  widths: Record<string, number>,
): Record<string, string> {
  const out: Record<string, string> = {}
  for (const id of order) {
    const w = widths[id]
    out[id] = typeof w === 'number' && Number.isFinite(w) ? String(w) : ''
  }
  return out
}

/**
 * Итоговый `widths` для prefs: пустое поле — убрать переопределение (как у таблицы по умолчанию);
 * число — записать с clamp.
 */
export function mergeColumnWidthsFromDraft(
  base: Record<string, number>,
  order: readonly string[],
  draft: Record<string, string>,
): Record<string, number> {
  const next: Record<string, number> = { ...base }
  for (const id of order) {
    const raw = (draft[id] ?? '').trim()
    if (raw === '') {
      delete next[id]
      continue
    }
    const n = Math.round(Number(raw))
    if (Number.isFinite(n)) next[id] = clampListColumnWidthPx(n)
    else delete next[id]
  }
  return next
}
