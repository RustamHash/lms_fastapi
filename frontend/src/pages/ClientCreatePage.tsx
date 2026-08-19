import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiFetch } from '../lib/http'

export function ClientCreatePage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    depositor_id: '',
    external_id: '',
    name: '',
    legal_name: '',
    inn: '',
    kpp: '',
    is_edo: false,
  })
  const [depositors, setDepositors] = useState<{id: number, code: string}[]>([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    ;(async () => {
      const res = await apiFetch('/api/v1/parties/depositors')
      if (res.ok) setDepositors(await res.json())
    })()
  }, [])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      const res = await apiFetch('/api/v1/parties/clients', {
        method: 'POST',
        body: JSON.stringify({
          ...form,
          depositor_id: Number(form.depositor_id),
        }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const created = await res.json()
      navigate(`/reference/clients/${created.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка')
    } finally {
      setSaving(false)
    }
  }

  function set(field: string, value: string | boolean) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  return (
    <section className="app-card app-card--wide">
      <h1 className="page-title">Новый клиент</h1>
      <form onSubmit={onSubmit} className="wh-form">
        <label>Поклажедатель *
          <select value={form.depositor_id} onChange={(e) => set('depositor_id', e.target.value)} required>
            <option value="">— выберите —</option>
            {depositors.map((d) => <option key={d.id} value={d.id}>{d.code}</option>)}
          </select>
        </label>
        <label>Внешний код *<input value={form.external_id} onChange={(e) => set('external_id', e.target.value)} required /></label>
        <label>Наименование *<input value={form.name} onChange={(e) => set('name', e.target.value)} required /></label>
        <label>Полное наименование<input value={form.legal_name} onChange={(e) => set('legal_name', e.target.value)} /></label>
        <label>ИНН<input value={form.inn} onChange={(e) => set('inn', e.target.value)} /></label>
        <label>КПП<input value={form.kpp} onChange={(e) => set('kpp', e.target.value)} /></label>
        <label className="wh-form__check"><input type="checkbox" checked={form.is_edo} onChange={(e) => set('is_edo', e.target.checked)} /> ЭДО</label>
        {error ? <p className="wh-form__err">{error}</p> : null}
        <div className="wh-form__actions">
          <button type="submit" disabled={saving}>{saving ? 'Создание...' : 'Создать'}</button>
          <button type="button" onClick={() => navigate('/reference/clients')}>Отмена</button>
        </div>
      </form>
    </section>
  )
}
