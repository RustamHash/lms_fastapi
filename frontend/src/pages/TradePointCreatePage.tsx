import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../lib/apiClient'

export function TradePointCreatePage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ client_id: '', address_id: '', name: '' })
  const [clients, setClients] = useState<{id: number, name: string}[]>([])
  const [addresses, setAddresses] = useState<{id: number, full_address: string}[]>([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    ;(async () => {
      const [clientsData, addressesData] = await Promise.all([
        apiClient.get<{id: number, name: string}[]>('/api/v1/parties/clients'),
        apiClient.get<{id: number, full_address: string}[]>('/api/v1/parties/addresses/list'),
      ])
      setClients(clientsData)
      setAddresses(addressesData)
    })()
  }, [])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      const created = await apiClient.post<{id: number}>('/api/v1/parties/trade-points/resolve', {
        client_id: Number(form.client_id),
        address_id: Number(form.address_id),
        name: form.name,
      })
      navigate(`/reference/trade-points/${created.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка')
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="app-card app-card--wide">
      <h1 className="page-title">Новая торговая точка</h1>
      <form onSubmit={onSubmit} className="wh-form">
        <label>Клиент *
          <select value={form.client_id} onChange={(e) => setForm((p) => ({...p, client_id: e.target.value}))} required>
            <option value="">— выберите —</option>
            {clients.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </label>
        <label>Адрес *
          <select value={form.address_id} onChange={(e) => setForm((p) => ({...p, address_id: e.target.value}))} required>
            <option value="">— выберите —</option>
            {addresses.map((a) => <option key={a.id} value={a.id}>{a.full_address}</option>)}
          </select>
        </label>
        <label>Название<input value={form.name} onChange={(e) => setForm((p) => ({...p, name: e.target.value}))} /></label>
        {error ? <p className="wh-form__err">{error}</p> : null}
        <div className="wh-form__actions">
          <button type="submit" disabled={saving}>{saving ? 'Создание...' : 'Создать'}</button>
          <button type="button" onClick={() => navigate('/reference/trade-points')}>Отмена</button>
        </div>
      </form>
    </section>
  )
}
