/**
 * Общие типы фильтров списков.
 * UI пока остаётся строковым; операторы задел под будущие даты/числа/операторы как в 1С.
 * Сопоставление строки с строкой — через filterEngine (legacy «содержит» и расширения).
 */

/** Значение фильтра «только пустая дата» (контекстное меню и т.п.) */
export const LIST_FILTER_EMPTY_DATE = '__ss_empty__'

/** Текстовые операторы (будущий UI) */
export type TextFilterOp =
  | 'contains'
  | 'equals'
  | 'not_contains'
  | 'starts_with'
  | 'ends_with'

/** Числовые операторы (заказы, вес, количество) */
export type NumberFilterOp = 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'between'

/** Операторы по дате/времени */
export type DateTimeFilterOp = 'before' | 'after' | 'between' | 'is_empty' | 'is_not_empty'

export type TextFilterState = {
  op: TextFilterOp
  value: string
}

export type NumberFilterState = {
  op: NumberFilterOp
  /** Строка с поля ввода; парсинг в filterEngine */
  value: string
  valueTo?: string
}

export type DateTimeFilterState = {
  op: DateTimeFilterOp
  value?: string
  valueTo?: string
}

/** Тип колонки для выбора набора операторов в будущем UI */
export type ListColumnFilterKind = 'text' | 'number' | 'datetime' | 'select' | 'bool'

/** Состояние фильтра одной колонки (полная модель на будущее) */
export type ColumnFilterState =
  | { kind: 'text'; text: TextFilterState }
  | { kind: 'number'; number: NumberFilterState }
  | { kind: 'datetime'; datetime: DateTimeFilterState }
  | { kind: 'select'; value: string }
