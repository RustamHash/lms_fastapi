import {
  LIST_COL_MEASURE_MAX_CHARS,
  clampListColumnWidthPx,
} from '../features/lists/columnWidthConstants'

/** Сжать строку для измерения ширины (длинный текст + «…»). */
export function clipTextForColumnMeasure(s: string): string {
  const t = String(s).replace(/\s+/g, ' ').trim()
  if (t.length === 0) return ' '
  if (t.length <= LIST_COL_MEASURE_MAX_CHARS) return t
  return `${t.slice(0, LIST_COL_MEASURE_MAX_CHARS)}…`
}

export function measureStringWidthPx(text: string, font: string): number {
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  if (!ctx) return 0
  ctx.font = font
  return ctx.measureText(text).width
}

const HEADER_FONT = '500 11px system-ui, -apple-system, "Segoe UI", sans-serif'
const CELL_FONT = 'normal 11px system-ui, -apple-system, "Segoe UI", sans-serif'

/** Доп. место под стрелку сортировки и отступы шапки (px). */
const HEADER_EXTRA_PX = 28
/** Горизонтальные отступы ячейки + границы (прибл., px). */
const CELL_EXTRA_PX = 14

/**
 * Ширина колонки по заголовку и текстам строк (с ограничением max и усечением длинных строк).
 */
export function computeAutoFitColumnWidthPx(
  headerLabel: string,
  rowTexts: readonly string[],
): number {
  let maxInner = 0
  const h = clipTextForColumnMeasure(headerLabel)
  maxInner = Math.max(maxInner, measureStringWidthPx(h, HEADER_FONT) + HEADER_EXTRA_PX)
  for (const raw of rowTexts) {
    const t = clipTextForColumnMeasure(raw)
    maxInner = Math.max(maxInner, measureStringWidthPx(t, CELL_FONT) + CELL_EXTRA_PX)
  }
  return clampListColumnWidthPx(Math.ceil(maxInner))
}
