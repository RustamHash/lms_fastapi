import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../lib/apiClient'

export function ContractCreatePage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    number: '',
    customer_id: '',
    executor_id: '',
    contract_type: 'storage',
    start_date: '',
    end_date: '',
  })
  const [legalEntities, setLegalEntities] = useState<{id: number, name: string}[]>([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    ;(async () => {
      const entitiesData = await apiClient.get<{id: number, name: string}[]>('/api/v1/legal-entities')
      setLegalEntities(entitiesData)
    })()
  }, [])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      const created = await apiClient.post<{id: number}>('/api/v1/contracts', {
        number: form.number,
        customer_id: Number(form.customer_id),
        executor_id: Number(form.executor_id),
        contract_type: form.contract_type,
        start_date: form.start_date,
        end_date: form.end_date || null,
      })
      navigate(`/reference/contracts/${created.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка')
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="app-card app-card--wide">
      <h1 className="page-title">Новый договор</h1>
      <form onSubmit={onSubmit} className="wh-form">
        <label>Номер *<input value={form.number} onChange={(e) => setForm((p) => ({...p, number: e.target.value}))} required /></label>
        <label>Заказчик *
          <select value={form.customer_id} onChange={(e) => setForm((p) => ({...p, customer_id: e.target.value}))} required>
            <option value="">— выберите —</option>
            {legalEntities.map((le) => <option key={le.id} value={le.id}>{le.name}</option>)}
          </select>
        </label>
        <label>Исполнитель *
          <select value={form.executor_id} onChange={(e) => setForm((p) => ({...p, executor_id: e.target.value}))} required>
            <option value="">— выберите —</option>
            {legalEntities.map((le) => <option key={le.id} value={le.id}>{le.name}</option>)}
          </select>
        </label>
        <label>Тип
          <select value={form.contract_type} onChange={(e) => setForm((p) => ({...p, contract_type: e.target.value}))}>
            <option value="storage">Хранение</option>
            <option value="delivery">Доставка</option>
            <option value="services">Услуги</option>
          </select>
        </label>
        <label>Дата начала *<input type="date" value={form.start_date} onChange={(e) => setForm((p) => ({...p, start_date: e.target.value}))} required /></label>
        <label>Дата окончания<input type="date" value={form.end_date} onChange={(e) => setForm((p) => ({...p, end_date: e.target.value}))} /></label>
        {error ? <p className="wh-form__err">{error}</p> : null}
        <div className="wh-form__actions">
          <button type="submit" disabled={saving}>{saving ? 'Создание...' : 'Создать'}</button>
          <button type="button" onClick={() => navigate('/reference/contracts')}>Отмена</button>
        </div>
      </form>
    </section>
  )
}
