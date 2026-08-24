import { useCallback, useEffect, useState } from 'react'
import { apiClient } from '../../../lib/apiClient'

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
        const data = await apiClient.get<T>(`${apiUrl}/${id}`)
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
      const updated = await apiClient.patch<T>(`${apiUrl}/${id}`, patch)
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
      await apiClient.delete(`${apiUrl}/${id}`)
    } finally {
      setDeleting(false)
    }
  }, [apiUrl, id])
  
  useEffect(() => {
    if (id > 0) {
      const timer = setTimeout(() => void load(), 0)
      return () => clearTimeout(timer)
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
