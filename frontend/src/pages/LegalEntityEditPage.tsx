import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { apiFetch } from '../lib/http'

export function LegalEntityEditPage() {
  const { entityId } = useParams<{ entityId: string }>()
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
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!entityId) return
    ;(async () => {
      setLoading(true)
      try {
        const res = await apiFetch(`/api/v1/parties/legal-entities/${entityId}`)
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = await res.json()
        setForm({
          name: data.name,
          legal_name: data.legal_name,
          inn: data.inn,
          kpp: data.kpp,
          ogrn: data.ogrn,
          phone: data.phone,
          email: data.email,
        })
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Ошибка')
      } finally {
        setLoading(false)
      }
    })()
  }, [entityId])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      const res = await apiFetch(`/api/v1/parties/legal-entities/${entityId}`, {
        method: 'PATCH',
        body: JSON.stringify(form),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      navigate(`/reference/legal-entities/${entityId}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка')
    } finally {
      setSaving(false)
    }
  }

  function set(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  if (loading) return <p>Загрузка...</p>

  return (
    <section className="app-card app-card--wide">
      <h1 className="page-title">Редактирование юрлица</h1>
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
          <button type="submit" disabled={saving}>{saving ? 'Сохранение...' : 'Сохранить'}</button>
          <button type="button" onClick={() => navigate(`/reference/legal-entities/${entityId}`)}>Отмена</button>
        </div>
      </form>
    </section>
  )
}
