import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiFetch } from '../lib/http'

export function LegalEntityCreatePage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: '',
    legal_name: '',
    inn: '',
    kpp: '',
    ogrn: '',
    phone: '',
    email: '',
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      const res = await apiFetch('/api/v1/parties/legal-entities', {
        method: 'POST',
        body: JSON.stringify(form),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const created = await res.json()
      navigate(`/reference/legal-entities/${created.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка')
    } finally {
      setSaving(false)
    }
  }

  function set(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  return (
    <section className="app-card app-card--wide">
      <h1 className="page-title">Новое юрлицо</h1>
      <form onSubmit={onSubmit} className="wh-form">
        <label>Наименование *<input value={form.name} onChange={(e) => set('name', e.target.value)} required /></label>
        <label>Полное наименование<input value={form.legal_name} onChange={(e) => set('legal_name', e.target.value)} /></label>
        <label>ИНН<input value={form.inn} onChange={(e) => set('inn', e.target.value)} /></label>
        <label>КПП<input value={form.kpp} onChange={(e) => set('kpp', e.target.value)} /></label>
        <label>ОГРН<input value={form.ogrn} onChange={(e) => set('ogrn', e.target.value)} /></label>
        <label>Телефон<input value={form.phone} onChange={(e) => set('phone', e.target.value)} /></label>
        <label>Email<input type="email" value={form.email} onChange={(e) => set('email', e.target.value)} /></label>
        {error ? <p className="wh-form__err">{error}</p> : null}
        <div className="wh-form__actions">
          <button type="submit" disabled={saving}>{saving ? 'Создание...' : 'Создать'}</button>
          <button type="button" onClick={() => navigate('/reference/legal-entities')}>Отмена</button>
        </div>
      </form>
    </section>
  )
}
