import { useCallback, useEffect, useMemo, useState } from 'react'
import { apiClient } from '../lib/apiClient'
import type { TablePrefs } from './useTableSettings'

export type ListPreset = {
  id: number
  name: string
  config: TablePrefs
  is_default: boolean
  created_at: string
  updated_at: string
}

export function useListPresets(entityKey: string) {
  const [presets, setPresets] = useState<ListPreset[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await apiClient.get<ListPreset[]>(`/api/v1/list-presets/${entityKey}`)
      setPresets(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка загрузки пресетов')
    } finally {
      setLoading(false)
    }
  }, [entityKey])

  const createPreset = useCallback(async (name: string, config: TablePrefs, isDefault = false): Promise<ListPreset> => {
    const res = await apiClient.post(`/api/v1/list-presets/${entityKey}`, { name, config, is_default: isDefault })
    if (!res.ok) {
      const data = await res.json().catch(() => null)
      throw new Error(data?.detail ?? `HTTP ${res.status}`)
    }
    const preset = await res.json() as ListPreset
    setPresets(prev => [...prev, preset])
    return preset
  }, [entityKey])

  const updatePreset = useCallback(async (presetId: number, name: string, config: TablePrefs): Promise<ListPreset> => {
    const res = await apiClient.put(`/api/v1/list-presets/${entityKey}/${presetId}`, { name, config })
    if (!res.ok) {
      const data = await res.json().catch(() => null)
      throw new Error(data?.detail ?? `HTTP ${res.status}`)
    }
    const preset = await res.json() as ListPreset
    setPresets(prev => prev.map(p => p.id === presetId ? preset : p))
    return preset
  }, [entityKey])

  const deletePreset = useCallback(async (presetId: number): Promise<void> => {
    const res = await apiClient.delete(`/api/v1/list-presets/${entityKey}/${presetId}`)
    if (!res.ok && res.status !== 204) throw new Error(`HTTP ${res.status}`)
    setPresets(prev => prev.filter(p => p.id !== presetId))
  }, [entityKey])

  const applyPreset = useCallback(async (presetId: number): Promise<TablePrefs> => {
    const res = await apiClient.post(`/api/v1/list-presets/${entityKey}/${presetId}/apply`)
    if (!res.ok) {
      const data = await res.json().catch(() => null)
      throw new Error(data?.detail ?? `HTTP ${res.status}`)
    }
    const data = await res.json() as { prefs: TablePrefs }
    return data.prefs
  }, [entityKey])

  const setDefaultPreset = useCallback(async (presetId: number): Promise<ListPreset> => {
    const res = await apiClient.post(`/api/v1/list-presets/${entityKey}/${presetId}/set-default`)
    if (!res.ok) {
      const data = await res.json().catch(() => null)
      throw new Error(data?.detail ?? `HTTP ${res.status}`)
    }
    const preset = await res.json() as ListPreset
    setPresets(prev => prev.map(p => ({ ...p, is_default: p.id === presetId })))
    return preset
  }, [entityKey])

  useEffect(() => {
    const timer = setTimeout(() => void load(), 0)
    return () => clearTimeout(timer)
  }, [load])

  return useMemo(() => ({
    presets,
    loading,
    error,
    createPreset,
    updatePreset,
    deletePreset,
    applyPreset,
    setDefaultPreset,
    reload: load,
  }), [presets, loading, error, createPreset, updatePreset, deletePreset, applyPreset, setDefaultPreset, load])
}
