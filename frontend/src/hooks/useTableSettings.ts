import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { apiClient } from '../lib/apiClient'

export type TablePrefs = {
  order: string[]
  hidden: string[]
  widths: Record<string, number>
  filters: Record<string, string>
  exclude_filters: Record<string, string[]>
  sort: { column: string | null; direction: 'asc' | 'desc' } | null
  quick_filters: string[]
}

type TableSettingsResponse = {
  prefs: TablePrefs
}

export function useTableSettings(entityKey: string) {
  const [prefs, setPrefs] = useState<TablePrefs | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiClient.get<TableSettingsResponse>(`/api/v1/table-settings/${entityKey}`)
      setPrefs(data.prefs)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка загрузки настроек')
    } finally {
      setLoading(false)
    }
  }, [entityKey])

  const save = useCallback(async (nextPrefs: TablePrefs) => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current)
    }
    
    debounceTimerRef.current = setTimeout(async () => {
      try {
        const res = await apiClient.put(`/api/v1/table-settings/${entityKey}`, { prefs: nextPrefs })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = await res.json() as TableSettingsResponse
        setPrefs(data.prefs)
      } catch (e) {
        console.error('Ошибка сохранения настроек:', e)
      }
    }, 500)
  }, [entityKey])

  const resetToDefaults = useCallback(async (): Promise<TablePrefs> => {
    const res = await apiClient.get(`/api/v1/table-settings/${entityKey}/defaults`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json() as TableSettingsResponse
    setPrefs(data.prefs)
    return data.prefs
  }, [entityKey])

  const clear = useCallback(async () => {
    const res = await apiClient.delete(`/api/v1/table-settings/${entityKey}`)
    if (!res.ok && res.status !== 204) throw new Error(`HTTP ${res.status}`)
    setPrefs(null)
  }, [entityKey])

  useEffect(() => {
    const timer = setTimeout(() => void load(), 0)
    return () => {
      clearTimeout(timer)
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current)
      }
    }
  }, [load])

  return useMemo(() => ({
    prefs,
    loading,
    error,
    save,
    resetToDefaults,
    clear,
    reload: load,
  }), [prefs, loading, error, save, resetToDefaults, clear, load])
}
