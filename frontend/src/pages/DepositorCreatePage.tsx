import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiFetch } from '../lib/http'

export function DepositorCreatePage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ code: '', legal_entity_id: '' })
  const [legalEntities, setLegalEntities] = useState<{id: number, name: string}[]>([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    ;(async () => {
      const res = await apiFetch('/api/v1/parties/legal-entities')
      if (res.ok) setLegalEntities(await res.json())
    })()
  }, [])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      const res = await apiFetch('/api/v1/parties/depositors', {
        method: 'POST',
        body: JSON.stringify({
          code: form.code,
          legal_entity_id: Number(form.legal_entity_id),
        }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const created = await res.json()
      navigate(`/reference/depositors/${created.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка')
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="app-card app-card--wide">
      <h1 className="page-title">Новый поклажедатель</h1>
      <form onSubmit={onSubmit} className="wh-form">
        <label>Код<input value={form.code} onChange={(e) => setForm((p) => ({...p, code: e.target.value}))} /></label>
        <label>Юрлицо *
          <select value={form.legal_entity_id} onChange={(e) => setForm((p) => ({...p, legal_entity_id: e.target.value}))} required>
            <option value="">— выберите —</option>
            {legalEntities.map((le) => <option key={le.id} value={le.id}>{le.name}</option>)}
          </select>
        </label>
        {error ? <p className="wh-form__err">{error}</p> : null}
        <div className="wh-form__actions">
          <button type="submit" disabled={saving}>{saving ? 'Создание...' : 'Создать'}</button>
          <button type="button" onClick={() => navigate('/reference/depositors')}>Отмена</button>
        </div>
      </form>
    </section>
  )
}
