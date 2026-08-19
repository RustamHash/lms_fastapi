import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { apiFetch } from '../lib/http'
import { clampListColumnWidthPx } from '../features/lists/columnWidthConstants'

export type ColumnDef = { id: string; label: string }

export type PrefsPayload = { order: string[]; hidden: string[]; widths: Record<string, number> }

type ApiGetResponse = { prefs: PrefsPayload | null }

/** Сливает ответ сервера с дефолтным списком колонок: новые поля в конец, чужие id отбрасываются. */
function mergePrefs(
  defaults: readonly ColumnDef[],
  saved: Partial<PrefsPayload> | null,
  defaultHiddenColumnIds: readonly string[],
): PrefsPayload {
  const allowed = new Set(defaults.map((c) => c.id))
  const defaultHiddenSet = new Set(defaultHiddenColumnIds.filter((id) => allowed.has(id)))
  const prevOrder = (saved?.order ?? []).filter((id) => allowed.has(id))
  const prevOrderSet = new Set(prevOrder)

  const order = [...prevOrder]
  for (const c of defaults) {
    if (!order.includes(c.id)) order.push(c.id)
  }

  let hidden: string[]
  if (saved == null) {
    hidden = defaults.filter((c) => defaultHiddenSet.has(c.id)).map((c) => c.id)
  } else {
    const base = (saved.hidden ?? []).filter((id) => allowed.has(id))
    const hiddenSet = new Set(base)
    for (const c of defaults) {
      if (!prevOrderSet.has(c.id) && defaultHiddenSet.has(c.id)) {
        hiddenSet.add(c.id)
      }
    }
    hidden = [...hiddenSet]
  }
  const widths: Record<string, number> = {}
  const rawW = saved?.widths
  if (rawW && typeof rawW === 'object') {
    for (const id of allowed) {
      const v = rawW[id]
      if (typeof v === 'number' && Number.isFinite(v)) {
        widths[id] = clampListColumnWidthPx(v)
      }
    }
  }
  return { order, hidden, widths }
}

function emptyPrefs(defaults: readonly ColumnDef[], defaultHiddenColumnIds: readonly string[]): PrefsPayload {
  return mergePrefs(defaults, null, defaultHiddenColumnIds)
}

/**
 * Загрузка/сохранение порядка, скрытых колонок и ширин на сервере (таблица ui_list_preferences).
 * entityKey — одна строка на экран (например "warehouses").
 * defaultHiddenColumnIds — id колонок, скрытых по умолчанию (пока нет сохранённых prefs и для новых колонок после обновления).
 */
export function useColumnPrefs(
  entityKey: string,
  defaults: readonly ColumnDef[],
  defaultHiddenColumnIds: readonly string[] = [],
) {
  const defaultsSig = useMemo(
    () => defaults.map((c) => `${c.id}:${c.label}`).join('|'),
    [defaults],
  )
  const defaultHiddenSig = useMemo(
    () => [...defaultHiddenColumnIds].join('|'),
    [defaultHiddenColumnIds],
  )
  const defaultsRef = useRef(defaults)
  const defaultHiddenRef = useRef(defaultHiddenColumnIds)
  useEffect(() => {
    defaultsRef.current = defaults
    defaultHiddenRef.current = defaultHiddenColumnIds
  }, [defaultsSig, defaultHiddenSig, defaults, defaultHiddenColumnIds])

  const [order, setOrder] = useState<string[]>(
    () => emptyPrefs(defaultsRef.current, defaultHiddenRef.current).order,
  )
  const [hidden, setHidden] = useState<string[]>(
    () => emptyPrefs(defaultsRef.current, defaultHiddenRef.current).hidden,
  )
  const [widths, setWidths] = useState<Record<string, number>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const lastAutoLoadKeyRef = useRef<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const url = `/api/v1/table-settings/${encodeURIComponent(entityKey)}`
      const res = await apiFetch(url)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = (await res.json()) as ApiGetResponse
      const m = mergePrefs(defaultsRef.current, data.prefs, defaultHiddenRef.current)
      setOrder(m.order)
      setHidden(m.hidden)
      setWidths(m.widths)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка загрузки настроек колонок')
      const m = mergePrefs(defaultsRef.current, null, defaultHiddenRef.current)
      setOrder(m.order)
      setHidden(m.hidden)
      setWidths(m.widths)
    } finally {
      setLoading(false)
    }
  }, [entityKey, defaultsSig, defaultHiddenSig])

  const autoLoadKey = `${entityKey}::${defaultsSig}::${defaultHiddenSig}`
  useEffect(() => {
    if (lastAutoLoadKeyRef.current === autoLoadKey) return
    lastAutoLoadKeyRef.current = autoLoadKey
    void load()
  }, [autoLoadKey, load])

  const savePrefs = useCallback(
    async (next: PrefsPayload) => {
      const url = `/api/v1/table-settings/${encodeURIComponent(entityKey)}`
      const res = await apiFetch(url, {
        method: 'PUT',
        body: JSON.stringify(next),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = (await res.json()) as { prefs: PrefsPayload }
      if (data.prefs) {
        const m = mergePrefs(defaultsRef.current, data.prefs, defaultHiddenRef.current)
        setOrder(m.order)
        setHidden(m.hidden)
        setWidths(m.widths)
      }
    },
    [entityKey, defaultsSig, defaultHiddenSig],
  )

  const hiddenSet = new Set(hidden)
  const visibleOrderedIds = order.filter((id) => !hiddenSet.has(id))

  return {
    order,
    hidden,
    widths,
    hiddenSet,
    visibleOrderedIds,
    loading,
    error,
    setOrder,
    setHidden,
    savePrefs,
    reload: load,
  }
}
