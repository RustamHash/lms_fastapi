import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { apiClient } from '../lib/apiClient'

export function DepositorEditPage() {
  const { depositorId } = useParams<{ depositorId: string }>()
  const navigate = useNavigate()
  const [form, setForm] = useState({ code: '', legal_entity_id: '' })
  const [legalEntities, setLegalEntities] = useState<{ id: number; name: string }[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!depositorId) return
    ;(async () => {
      setLoading(true)
      try {
        const [depositorData, legalEntitiesData] = await Promise.all([
          apiClient.get<{ code: string; legal_entity_id: number }>(`/api/v1/depositors/${depositorId}`),
          apiClient.get<{ id: number; name: string }[]>('/api/v1/legal-entities'),
        ])
        setForm({ code: depositorData.code, legal_entity_id: String(depositorData.legal_entity_id) })
        setLegalEntities(legalEntitiesData)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Ошибка загрузки')
      } finally {
        setLoading(false)
      }
    })()
  }, [depositorId])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      await apiClient.patch(`/api/v1/depositors/${depositorId}`, {
        code: form.code,
        legal_entity_id: Number(form.legal_entity_id),
      })
      navigate(`/reference/depositors/${depositorId}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка сохранения')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <p>Загрузка...</p>

  return (
    <section className="app-card app-card--wide">
      <h1 className="page-title">Редактирование поклажедателя</h1>
      <form onSubmit={onSubmit} className="wh-form">
        <label>Код *<input value={form.code} onChange={(e) => setForm((p) => ({...p, code: e.target.value}))} required /></label>
        <label>Юрлицо *
          <select
            value={form.legal_entity_id}
            onChange={(e) => setForm((p) => ({...p, legal_entity_id: e.target.value}))}
            required
            onInvalid={(e) => {
              const target = e.target as HTMLSelectElement
              target.setCustomValidity('Выберите юридическое лицо')
            }}
            onInput={(e) => {
              const target = e.target as HTMLSelectElement
              target.setCustomValidity('')
            }}
          >
            <option value="">— выберите —</option>
            {legalEntities.map((le) => (
              <option key={le.id} value={le.id}>{le.name}</option>
            ))}
          </select>
        </label>
        {error ? <p className="wh-form__err">{error}</p> : null}
        <div className="wh-form__actions">
          <button type="submit" disabled={saving}>{saving ? 'Сохранение...' : 'Сохранить'}</button>
          <button type="button" onClick={() => navigate(`/reference/depositors/${depositorId}`)}>Отмена</button>
        </div>
      </form>
    </section>
  )
}
