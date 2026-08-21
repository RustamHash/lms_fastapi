import { useState } from 'react'
import type { TablePrefs } from '../hooks/useTableSettings'

type Props = {
  entityKey: string
  currentPrefs: TablePrefs
  onSave: (name: string, config: TablePrefs, isDefault: boolean) => Promise<void>
  onClose: () => void
}

export function SavePresetDialog({ currentPrefs, onSave, onClose }: Props) {
  const [name, setName] = useState('')
  const [isDefault, setIsDefault] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) return
    
    setSaving(true)
    setError(null)
    try {
      await onSave(name.trim(), currentPrefs, isDefault)
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка сохранения')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="dialog-backdrop" role="presentation">
      <div className="dialog" role="dialog" aria-modal="true" aria-labelledby="save-preset-title">
        <h3 id="save-preset-title" className="dialog__title">Сохранить пресет</h3>
        
        <form onSubmit={handleSubmit}>
          <div className="wh-form">
            <label>
              Название пресета *
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Например: Мои активные клиенты"
                required
                autoFocus
              />
            </label>
            
            <label className="wh-form__check">
              <input
                type="checkbox"
                checked={isDefault}
                onChange={(e) => setIsDefault(e.target.checked)}
              />
              Использовать по умолчанию
            </label>
            
            {error ? <p className="wh-form__err">{error}</p> : null}
            
            <div className="wh-form__actions">
              <button type="submit" className="tb tb--create" disabled={saving || !name.trim()}>
                {saving ? 'Сохранение...' : 'Сохранить'}
              </button>
              <button type="button" className="tb tb--reset" onClick={onClose} data-close="true">
                Отмена
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}
