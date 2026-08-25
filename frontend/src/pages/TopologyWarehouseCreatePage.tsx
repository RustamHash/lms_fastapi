import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../lib/apiClient'

type AddressOption = { id: number; full_address: string }

export function TopologyWarehouseCreatePage() {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [addressId, setAddressId] = useState('')
  const [addresses, setAddresses] = useState<AddressOption[]>([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    void (async () => {
      try {
        const data = await apiClient.get<AddressOption[]>('/api/v1/addresses')
        setAddresses(data)
      } catch {
        setAddresses([])
      }
    })()
  }, [])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) return

    setSaving(true)
    setError(null)
    try {
      const created = await apiClient.post<{ id: number }>(
        '/api/v1/warehouse/topology/warehouses',
        {
          name: name.trim(),
          address_id: addressId ? Number(addressId) : null,
        },
      )
      navigate(`/topology/warehouses/${created.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка')
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="app-card app-card--wide">
      <h1 className="page-title">Новый склад</h1>
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
        <label>
          Адрес
          <select value={addressId} onChange={(e) => setAddressId(e.target.value)}>
            <option value="">— не указан —</option>
            {addresses.map((a) => (
              <option key={a.id} value={a.id}>
                {a.full_address}
              </option>
            ))}
          </select>
        </label>
        {error ? <p className="wh-form__err">{error}</p> : null}
        <div className="wh-form__actions">
          <button type="submit" className="tb tb--create" disabled={saving}>
            {saving ? 'Создание...' : 'Создать'}
          </button>
          <button
            type="button"
            className="tb tb--reset"
            onClick={() => navigate('/topology/warehouses')}
          >
            Отмена
          </button>
        </div>
      </form>
    </section>
  )
}
