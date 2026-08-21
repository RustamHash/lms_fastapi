import { useState } from 'react'
import {
  decodeDateTimeFilter,
  encodeDateTimeFilter,
  type DateTimeFilterPayloadV1,
} from '../features/lists/dateTimeFilterCodec'
import { normalizeFilterDateTimeLocal } from '../features/lists/filterEngine'

type Props = {
  kind: 'text' | 'select' | 'datetime'
  value: string
  onChange: (next: string) => void
  options?: { value: string; label: string }[]
  'aria-label': string
  placeholder?: string
  /** Подсветка как у непустого фильтра (например, есть исключения по колонке). */
  highlightActive?: boolean
}

const DT_MODES: { m: DateTimeFilterPayloadV1['m']; label: string }[] = [
  { m: 'ct', label: 'Содержит' },
  { m: 'aft', label: 'После' },
  { m: 'bef', label: 'До' },
  { m: 'btw', label: 'Период' },
  { m: 'emp', label: 'Пусто' },
  { m: 'nem', label: 'Не пусто' },
]

function payloadFromValue(value: string): DateTimeFilterPayloadV1 {
  const d = decodeDateTimeFilter(value)
  if (!d) return { v: 1, m: 'ct', t: '' }
  const a = d.a != null && d.a.trim() !== '' ? normalizeFilterDateTimeLocal(d.a) : d.a
  const b = d.b != null && d.b.trim() !== '' ? normalizeFilterDateTimeLocal(d.b) : d.b
  return { ...d, a, b }
}

/** Для <input type="date">: из payload в YYYY-MM-DD. */
function filterValueToDateInput(s: string | undefined): string {
  if (s == null || !s.trim()) return ''
  return normalizeFilterDateTimeLocal(s.trim()).slice(0, 10)
}

export function ListFilterCell({
  kind,
  value,
  onChange,
  options,
  'aria-label': ariaLabel,
  placeholder = 'Фильтр',
  highlightActive = false,
}: Props) {
  const [dt, setDt] = useState<DateTimeFilterPayloadV1>(() => payloadFromValue(value))

  // Синхронизация через derived state при изменении value
  const currentDt = kind === 'datetime' ? payloadFromValue(value) : dt

  if (kind === 'datetime') {
    const activeDt = currentDt
    const dirty =
      activeDt.m === 'ct'
        ? (dt.t ?? '').trim() !== ''
        : dt.m === 'aft' || dt.m === 'bef'
          ? (dt.a ?? '').trim() !== ''
          : dt.m === 'btw'
            ? (dt.a ?? '').trim() !== '' || (dt.b ?? '').trim() !== ''
            : dt.m === 'emp' || dt.m === 'nem'

    function commit(next: DateTimeFilterPayloadV1) {
      let n = next
      if (next.m === 'aft' || next.m === 'bef') {
        const a = (next.a ?? '').trim() !== '' ? normalizeFilterDateTimeLocal(next.a ?? '') : next.a
        n = { ...next, a }
      } else if (next.m === 'btw') {
        const a = (next.a ?? '').trim() !== '' ? normalizeFilterDateTimeLocal(next.a ?? '') : next.a
        const b = (next.b ?? '').trim() !== '' ? normalizeFilterDateTimeLocal(next.b ?? '') : next.b
        n = { ...next, a, b }
      }
      setDt(n)
      const inactive =
        n.m === 'ct'
          ? (n.t ?? '').trim() === ''
          : n.m === 'aft' || n.m === 'bef'
            ? (n.a ?? '').trim() === ''
            : n.m === 'btw'
              ? (n.a ?? '').trim() === '' && (n.b ?? '').trim() === ''
              : false
      if (inactive && n.m !== 'emp' && n.m !== 'nem') {
        onChange('')
      } else {
        onChange(encodeDateTimeFilter(n))
      }
    }

    const activeStyle = dirty || highlightActive

    return (
      <div
        className={`list-filter-cell list-filter-cell--datetime${activeStyle ? ' list-filter-cell--dirty' : ''}`}
      >
        <div className="list-filter-cell__row">
          <select
            className="list-filter-cell__field list-filter-cell__field--select list-filter-cell__dt-op"
            value={activeDt.m}
            onChange={(e) => {
              const m = e.target.value as DateTimeFilterPayloadV1['m']
              commit({ v: 1, m, t: activeDt.t, a: activeDt.a, b: activeDt.b })
            }}
            aria-label={`${ariaLabel}: режим`}
          >
            {DT_MODES.map((o) => (
              <option key={o.m} value={o.m}>
                {o.label}
              </option>
            ))}
          </select>
          {dirty ? (
            <button
              type="button"
              className="list-filter-cell__clear list-filter-cell__clear--inline"
              onClick={() => {
                setDt({ v: 1, m: 'ct', t: '' })
                onChange('')
              }}
              aria-label={`Сбросить: ${ariaLabel}`}
              title="Сбросить фильтр"
            >
              ×
            </button>
          ) : null}
        </div>
        {dt.m === 'ct' ? (
          <input
            type="text"
            className="list-filter-cell__field list-filter-cell__dt-input"
            value={activeDt.t ?? ''}
            onChange={(e) => commit({ v: 1, m: 'ct', t: e.target.value })}
            placeholder={placeholder}
            aria-label={ariaLabel}
          />
        ) : null}
        {dt.m === 'aft' || dt.m === 'bef' ? (
          <input
            type="date"
            className="list-filter-cell__field list-filter-cell__dt-input"
            value={filterValueToDateInput(activeDt.a)}
            onChange={(e) => {
              const v = e.target.value
              commit({ v: 1, m: activeDt.m, a: v ? normalizeFilterDateTimeLocal(v) : '' })
            }}
            aria-label={ariaLabel}
          />
        ) : null}
        {dt.m === 'btw' ? (
          <div className="list-filter-cell__dt-range">
            <input
              type="date"
              className="list-filter-cell__field list-filter-cell__dt-input"
              value={filterValueToDateInput(activeDt.a)}
              onChange={(e) => {
                const v = e.target.value
                commit({ v: 1, m: 'btw', a: v ? normalizeFilterDateTimeLocal(v) : '', b: activeDt.b })
              }}
              aria-label={`${ariaLabel}: с`}
            />
            <input
              type="date"
              className="list-filter-cell__field list-filter-cell__dt-input"
              value={filterValueToDateInput(dt.b)}
              onChange={(e) => {
                const v = e.target.value
                commit({ v: 1, m: 'btw', a: activeDt.a, b: v ? normalizeFilterDateTimeLocal(v) : '' })
              }}
              aria-label={`${ariaLabel}: по`}
            />
          </div>
        ) : null}
      </div>
    )
  }

  const dirty = kind === 'text' ? value.trim() !== '' : value !== ''
  const activeStyle = dirty || highlightActive

  return (
    <div className={`list-filter-cell${activeStyle ? ' list-filter-cell--dirty' : ''}`}>
      <div className="list-filter-cell__row">
        {kind === 'text' ? (
          <input
            type="text"
            className="list-filter-cell__field"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            aria-label={ariaLabel}
          />
        ) : (
          <select
            className="list-filter-cell__field list-filter-cell__field--select"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            aria-label={ariaLabel}
          >
            {(options ?? []).map((o) => (
              <option key={o.value === '' ? '__all' : o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        )}
        {dirty ? (
          <button
            type="button"
            className="list-filter-cell__clear list-filter-cell__clear--inline"
            onClick={() => onChange('')}
            aria-label={`Сбросить: ${ariaLabel}`}
            title="Сбросить фильтр"
          >
            ×
          </button>
        ) : null}
      </div>
    </div>
  )
}
