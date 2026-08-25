import { useEffect, useState } from 'react'
import { apiClient } from '../../lib/apiClient'

type DeliveryZone = {
  id: number
  name: string
}

type Props = {
  value: number | null
  onChange: (value: number | null) => void
  allowEmpty?: boolean
  emptyLabel?: string
  disabled?: boolean
  required?: boolean
}

export function DeliveryZoneSelect({
  value,
  onChange,
  allowEmpty = true,
  emptyLabel = '— не назначена —',
  disabled = false,
  required = false,
}: Props) {
  const [zones, setZones] = useState<DeliveryZone[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await apiClient.get<DeliveryZone[]>('/api/v1/delivery-zones')
        if (!cancelled) setZones(data)
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Ошибка загрузки зон')
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  if (loading) return <select disabled><option>Загрузка зон…</option></select>
  if (error) return <p className="wh-form__err">{error}</p>

  return (
    <select
      value={value ?? ''}
      disabled={disabled}
      required={required}
      onChange={(e) => {
        const raw = e.target.value
        onChange(raw === '' ? null : Number(raw))
      }}
    >
      {allowEmpty ? <option value="">{emptyLabel}</option> : null}
      {zones.map((zone) => (
        <option key={zone.id} value={zone.id}>
          {zone.name}
        </option>
      ))}
    </select>
  )
}
