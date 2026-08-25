import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { DeliveryZoneSelect } from '../features/addresses/DeliveryZoneSelect'
import { apiClient } from '../lib/apiClient'

type AddressForm = {
  full_address: string
  region: string
  city: string
  street: string
  house: string
  building: string
  structure: string
  flat: string
  postal_code: string
  delivery_zone_id: number | null
  fias_id: string
  latitude: number | null
  longitude: number | null
}

export function AddressEditPage() {
  const { addressId } = useParams<{ addressId: string }>()
  const navigate = useNavigate()
  const [form, setForm] = useState<AddressForm>({
    full_address: '',
    region: '',
    city: '',
    street: '',
    house: '',
    building: '',
    structure: '',
    flat: '',
    postal_code: '',
    delivery_zone_id: null,
    fias_id: '',
    latitude: null,
    longitude: null,
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!addressId) return
    ;(async () => {
      setLoading(true)
      try {
        const data = await apiClient.get<AddressForm>(`/api/v1/addresses/${addressId}`)
        setForm({
          full_address: data.full_address,
          region: data.region ?? '',
          city: data.city ?? '',
          street: data.street ?? '',
          house: data.house ?? '',
          building: data.building ?? '',
          structure: data.structure ?? '',
          flat: data.flat ?? '',
          postal_code: data.postal_code ?? '',
          delivery_zone_id: data.delivery_zone_id ?? null,
          fias_id: data.fias_id ?? '',
          latitude: data.latitude ?? null,
          longitude: data.longitude ?? null,
        })
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Ошибка')
      } finally {
        setLoading(false)
      }
    })()
  }, [addressId])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      await apiClient.patch(`/api/v1/addresses/${addressId}`, {
        full_address: form.full_address,
        region: form.region,
        city: form.city,
        street: form.street,
        house: form.house,
        building: form.building,
        structure: form.structure,
        flat: form.flat,
        postal_code: form.postal_code,
        delivery_zone_id: form.delivery_zone_id,
      })
      navigate(`/reference/addresses/${addressId}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка')
    } finally {
      setSaving(false)
    }
  }

  function set(field: keyof AddressForm, value: string | number | null) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  if (loading) return <p>Загрузка...</p>

  return (
    <section className="app-card app-card--wide">
      <h1 className="page-title">Редактирование адреса</h1>
      <form onSubmit={onSubmit} className="wh-form">
        <label>
          Полный адрес *
          <input
            value={form.full_address}
            onChange={(e) => set('full_address', e.target.value)}
            required
          />
        </label>
        <label>
          Регион
          <input value={form.region} onChange={(e) => set('region', e.target.value)} />
        </label>
        <label>
          Город
          <input value={form.city} onChange={(e) => set('city', e.target.value)} />
        </label>
        <label>
          Улица
          <input value={form.street} onChange={(e) => set('street', e.target.value)} />
        </label>
        <label>
          Дом
          <input value={form.house} onChange={(e) => set('house', e.target.value)} />
        </label>
        <label>
          Корпус
          <input value={form.building} onChange={(e) => set('building', e.target.value)} />
        </label>
        <label>
          Строение
          <input value={form.structure} onChange={(e) => set('structure', e.target.value)} />
        </label>
        <label>
          Квартира
          <input value={form.flat} onChange={(e) => set('flat', e.target.value)} />
        </label>
        <label>
          Индекс
          <input value={form.postal_code} onChange={(e) => set('postal_code', e.target.value)} />
        </label>
        <label>
          Зона доставки
          <DeliveryZoneSelect
            value={form.delivery_zone_id}
            onChange={(value) => set('delivery_zone_id', value)}
          />
        </label>
        {form.fias_id ? (
          <label>
            ФИАС ID
            <input value={form.fias_id} readOnly disabled />
          </label>
        ) : null}
        {form.latitude != null ? (
          <label>
            Широта
            <input value={String(form.latitude)} readOnly disabled />
          </label>
        ) : null}
        {form.longitude != null ? (
          <label>
            Долгота
            <input value={String(form.longitude)} readOnly disabled />
          </label>
        ) : null}
        {error ? <p className="wh-form__err">{error}</p> : null}
        <div className="wh-form__actions">
          <button type="submit" disabled={saving}>
            {saving ? 'Сохранение...' : 'Сохранить'}
          </button>
          <button type="button" onClick={() => navigate(`/reference/addresses/${addressId}`)}>
            Отмена
          </button>
        </div>
      </form>
    </section>
  )
}
