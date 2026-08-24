import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../lib/apiClient'

export function IntegrationProfileCreatePage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: '',
    depositor_id: '',
    source_type: 'zln',
  })
  const [depositors, setDepositors] = useState<{ id: number; code: string }[]>([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    ;(async () => {
      const data = await apiClient.get<{ id: number; code: string }[]>('/api/v1/depositors')
      setDepositors(data)
    })()
  }, [])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      const created = await apiClient.post<{ id: number }>('/api/v1/integrations/profiles', {
        name: form.name,
        depositor_id: Number(form.depositor_id),
        source_type: form.source_type,
      })
      navigate(`/integrations/profiles/${created.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка')
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="app-card app-card--wide">
      <h1 className="page-title">Новый профиль интеграции</h1>
      <form onSubmit={onSubmit} className="wh-form">
        <label>Название *<input value={form.name} onChange={(e) => setForm((p) => ({...p, name: e.target.value}))} required /></label>
        <label>Поклажедатель
          <select value={form.depositor_id} onChange={(e) => setForm((p) => ({...p, depositor_id: e.target.value}))}>
            <option value="">— выберите —</option>
            {depositors.map((d) => (
              <option key={d.id} value={d.id}>{d.code}</option>
            ))}
          </select>
        </label>
        <label>Тип источника
          <select value={form.source_type} onChange={(e) => setForm((p) => ({...p, source_type: e.target.value}))}>
            <option value="zln">ZLN</option>
            <option value="manual">Ручной</option>
          </select>
        </label>
        {error ? <p className="wh-form__err">{error}</p> : null}
        <div className="wh-form__actions">
          <button type="submit" disabled={saving}>{saving ? 'Создание...' : 'Создать'}</button>
          <button type="button" onClick={() => navigate('/integrations/profiles')}>Отмена</button>
        </div>
      </form>
    </section>
  )
}
