import { useState } from 'react'
import { apiClient } from '../../lib/apiClient'
import { DeliveryZoneSelect } from './DeliveryZoneSelect'

type Props = {
  addressIds: number[]
  onComplete: (message: string) => void
  onCancel: () => void
}

export function AssignDeliveryZoneDialog({ addressIds, onComplete, onCancel }: Props) {
  const [zoneId, setZoneId] = useState<number | null>(null)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    const failures: string[] = []
    await Promise.all(
      addressIds.map(async (id) => {
        try {
          await apiClient.patch(`/api/v1/addresses/${id}`, { delivery_zone_id: zoneId })
        } catch (err) {
          failures.push(`#${id}: ${err instanceof Error ? err.message : 'ошибка'}`)
        }
      }),
    )
    setSaving(false)
    if (failures.length > 0) {
      setError(`Не удалось обновить ${failures.length} из ${addressIds.length}: ${failures.slice(0, 3).join('; ')}`)
      return
    }
    const msg =
      zoneId == null
        ? `Зона снята у ${addressIds.length} адрес(ов)`
        : `Зона назначена для ${addressIds.length} адрес(ов)`
    onComplete(msg)
  }

  return (
    <div className="dialog-backdrop" role="presentation">
      <div className="dialog" role="dialog" aria-modal="true">
        <h3 className="dialog__title">Назначить зону доставки</h3>
        <p className="dialog__text">
          Выбрано адресов: {addressIds.length}
        </p>
        <form onSubmit={(e) => void onSubmit(e)} className="wh-form">
          <label>
            Зона доставки
            <DeliveryZoneSelect
              value={zoneId}
              onChange={setZoneId}
            />
          </label>
          {error ? <p className="wh-form__err">{error}</p> : null}
          <div className="dialog__actions">
            <button type="submit" className="tb tb--create" disabled={saving}>
              {saving ? 'Сохранение…' : 'Применить'}
            </button>
            <button type="button" className="tb tb--reset" onClick={onCancel} disabled={saving}>
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
