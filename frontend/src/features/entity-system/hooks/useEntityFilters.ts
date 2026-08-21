import { useCallback, useMemo, useState } from 'react'

export function useEntityFilters() {
  const [filters, setFilters] = useState<Record<string, string>>({})
  const [excludeFilters, setExcludeFilters] = useState<Record<string, string[]>>({})
  const [quickFilters, setQuickFilters] = useState<string[]>([])

  const hasActiveFilters = useMemo(() => {
    const hasFilters = Object.values(filters).some(v => v !== '')
    const hasExcludes = Object.values(excludeFilters).some(arr => arr.some(v => v !== ''))
    return hasFilters || hasExcludes
  }, [filters, excludeFilters])

  const setFilter = useCallback((cid: string, value: string) => {
    setFilters(prev => {
      if (value === '') {
        const { [cid]: _removed, ...rest } = prev
        void _removed
        return rest
      }
      return { ...prev, [cid]: value }
    })
  }, [])

  const setExcludeFilter = useCallback((cid: string, value: string) => {
    setExcludeFilters(prev => {
      const cur = prev[cid] ?? []
      if (cur.includes(value)) return prev
      return { ...prev, [cid]: [...cur, value] }
    })
  }, [])

  const removeExcludeFilter = useCallback((cid: string, value: string) => {
    setExcludeFilters(prev => {
      const cur = prev[cid] ?? []
      return { ...prev, [cid]: cur.filter(v => v !== value) }
    })
  }, [])

  const resetFilters = useCallback(() => {
    setFilters({})
    setExcludeFilters({})
  }, [])

  const resetColumnFilter = useCallback((cid: string) => {
    setFilters(prev => {
      const { [cid]: _removed, ...rest } = prev
      void _removed
      return rest
    })
    setExcludeFilters(prev => {
      const { [cid]: _removed, ...rest } = prev
      void _removed
      return rest
    })
  }, [])

  return {
    filters,
    excludeFilters,
    quickFilters,
    setQuickFilters,
    hasActiveFilters,
    setFilter,
    setExcludeFilter,
    removeExcludeFilter,
    resetFilters,
    resetColumnFilter,
  }
}
