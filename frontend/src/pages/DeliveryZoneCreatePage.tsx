import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../lib/apiClient'

export function DeliveryZoneCreatePage() {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) return

    setSaving(true)
    setError(null)
    try {
      const created = await apiClient.post<{id: number}>('/api/v1/delivery-zones', { name: name.trim() })
      navigate(`/reference/delivery-zones/${created.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка')
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="app-card app-card--wide">
      <h1 className="page-title">Новая зона доставки</h1>
      <form onSubmit={handleSubmit} className="wh-form">
        <label>
          Название *
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            autoFocus
          />
        </label>
        {error ? <p className="wh-form__err">{error}</p> : null}
        <div className="wh-form__actions">
          <button type="submit" className="tb tb--create" disabled={saving}>
            {saving ? 'Создание...' : 'Создать'}
          </button>
          <button type="button" className="tb tb--reset" onClick={() => navigate('/reference/delivery-zones')}>
            Отмена
          </button>
        </div>
      </form>
    </section>
  )
}
