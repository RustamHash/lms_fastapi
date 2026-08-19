import { useCallback, useEffect, useState } from 'react'
import { apiFetch } from '../../../lib/http'

type UseEntityDetailParams = {
  entityKey: string
  apiUrl: string
  id: number
}

export function useEntityDetail<T extends { id: number }>({
  apiUrl,
  id,
}: UseEntityDetailParams) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editing, setEditing] = useState(false)
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)
  
  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await apiFetch(`${apiUrl}/${id}`)
      if (res.status === 404) {
        setError('Не найдено')
        return
      }
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json() as T
      setData(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка загрузки')
    } finally {
      setLoading(false)
    }
  }, [apiUrl, id])
  
  const save = useCallback(async (patch: Partial<T>): Promise<T> => {
    setSaving(true)
    try {
      const res = await apiFetch(`${apiUrl}/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patch),
      })
      if (!res.ok) {
        let detail = `HTTP ${res.status}`
        try {
          const body = await res.json() as { detail?: string }
          if (body?.detail) detail = body.detail
        } catch {
          // ignore
        }
        throw new Error(detail)
      }
      const updated = await res.json() as T
      setData(updated)
      setEditing(false)
      return updated
    } finally {
      setSaving(false)
    }
  }, [apiUrl, id])
  
  const remove = useCallback(async () => {
    setDeleting(true)
    try {
      const res = await apiFetch(`${apiUrl}/${id}`, { method: 'DELETE' })
      if (!res.ok) {
        let detail = `HTTP ${res.status}`
        try {
          const body = await res.json() as { detail?: string }
          if (body?.detail) detail = body.detail
        } catch {
          // ignore
        }
        throw new Error(detail)
      }
    } finally {
      setDeleting(false)
    }
  }, [apiUrl, id])
  
  useEffect(() => {
    if (id > 0) {
      void load()
    }
  }, [load, id])
  
  return {
    data,
    loading,
    error,
    editing,
    saving,
    deleting,
    setEditing,
    load,
    save,
    remove,
  }
}
