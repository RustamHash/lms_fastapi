import { useCallback, useEffect, useMemo, useState } from 'react'
import { apiClient } from '../../lib/apiClient'
import type { FlatField } from '../flattenFields'
import type { EntityFieldsResponse } from './types'
import { flattenFields, getDefaultFields, getDisplayableFields } from '../flattenFields'

/** Кэш метаданных: entity → поля */
const fieldsCache = new Map<string, EntityFieldsResponse>()

export function useEntityFields(entityKey: string) {
  const [fields, setFields] = useState<EntityFieldsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    // Проверить кэш
    if (fieldsCache.has(entityKey)) {
      setFields(fieldsCache.get(entityKey)!)
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)
    try {
      const data = await apiClient.get<EntityFieldsResponse>(
        `/api/v1/entities/${entityKey}/fields`,
      )
      fieldsCache.set(entityKey, data)
      setFields(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка загрузки метаданных')
    } finally {
      setLoading(false)
    }
  }, [entityKey])

  useEffect(() => {
    const timer = setTimeout(() => void load(), 0)
    return () => clearTimeout(timer)
  }, [load])

  const allFields: FlatField[] = useMemo(
    () => (fields ? flattenFields(fields.fields) : []),
    [fields],
  )
  const displayableFields: FlatField[] = useMemo(
    () => (fields ? getDisplayableFields(fields.fields) : []),
    [fields],
  )
  const defaultFields: FlatField[] = useMemo(
    () => (fields ? getDefaultFields(fields.fields) : []),
    [fields],
  )

  return {
    fields,
    allFields,
    displayableFields,
    defaultFields,
    loading,
    error,
    reload: load,
  }
}
