import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../lib/apiClient'

type DepositorOption = { id: number; code: string }
type WarehouseOption = { id: number; name: string }

export function TopologyVirtualWarehouseCreatePage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    depositor_id: '',
    warehouse_id: '',
    code: '',
    name: '',
  })
  const [depositors, setDepositors] = useState<DepositorOption[]>([])
  const [warehouses, setWarehouses] = useState<WarehouseOption[]>([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    void (async () => {
      try {
        const [depositorsData, warehousesData] = await Promise.all([
          apiClient.get<DepositorOption[]>('/api/v1/depositors'),
          apiClient.get<WarehouseOption[]>('/api/v1/warehouse/topology/warehouses'),
        ])
        setDepositors(depositorsData)
        setWarehouses(warehousesData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Не удалось загрузить справочники')
      }
    })()
  }, [])

  function set(field: keyof typeof form, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      const created = await apiClient.post<{ id: number }>(
        '/api/v1/warehouse/topology/virtual-warehouses',
        {
          depositor_id: Number(form.depositor_id),
          warehouse_id: Number(form.warehouse_id),
          code: form.code.trim(),
          name: form.name.trim(),
        },
      )
      navigate(`/topology/virtual-warehouses/${created.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка')
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="app-card app-card--wide">
      <h1 className="page-title">Новый виртуальный склад</h1>
      <form onSubmit={handleSubmit} className="wh-form">
        <label>
          Физический склад *
          <select
            value={form.warehouse_id}
            onChange={(e) => set('warehouse_id', e.target.value)}
            required
          >
            <option value="">— выберите —</option>
            {warehouses.map((w) => (
              <option key={w.id} value={w.id}>
                {w.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Поклажедатель *
          <select
            value={form.depositor_id}
            onChange={(e) => set('depositor_id', e.target.value)}
            required
          >
            <option value="">— выберите —</option>
            {depositors.map((d) => (
              <option key={d.id} value={d.id}>
                {d.code || `#${d.id}`}
              </option>
            ))}
          </select>
        </label>
        <label>
          Код *
          <input
            type="text"
            value={form.code}
            onChange={(e) => set('code', e.target.value)}
            required
            maxLength={50}
          />
        </label>
        <label>
          Наименование *
          <input
            type="text"
            value={form.name}
            onChange={(e) => set('name', e.target.value)}
            required
            autoFocus
          />
        </label>
        {error ? <p className="wh-form__err">{error}</p> : null}
        <div className="wh-form__actions">
          <button type="submit" className="tb tb--create" disabled={saving}>
            {saving ? 'Создание...' : 'Создать'}
          </button>
          <button
            type="button"
            className="tb tb--reset"
            onClick={() => navigate('/topology/virtual-warehouses')}
          >
            Отмена
          </button>
        </div>
      </form>
    </section>
  )
}
