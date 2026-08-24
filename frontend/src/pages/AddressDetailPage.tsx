import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { DetailPageShell } from '../components/DetailPageShell'
import { apiClient } from '../lib/apiClient'
import { formatDt } from '../lib/formatDt'

type AddressDetail = {
  id: number
  region: string
  city: string
  street: string
  house: string
  building: string | null
  structure: string | null
  flat: string | null
  postal_code: string | null
  full_address: string
  short_address: string
  full_address_with_postal_code: string
  delivery_zone_id: number | null
  delivery_zone: { id: number; name: string } | null
  zone_name: string | null
  fias_id: string | null
  latitude: number | null
  longitude: number | null
  source_raw: string | null
  created_at?: string
  updated_at?: string
}

export function AddressDetailPage() {
  const { addressId } = useParams<{ addressId: string }>()
  const idNum = addressId ? Number(addressId) : NaN
  const validId = Number.isInteger(idNum) && idNum > 0
  
  const [address, setAddress] = useState<AddressDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    if (!validId) {
      Promise.resolve().then(() => {
        setLoading(false)
        setError('Некорректный идентификатор')
      })
      return
    }
    
    let cancelled = false
    
    async function load() {
      setLoading(true)
      setError(null)
      try {
        const data = await apiClient.get<AddressDetail>(`/api/v1/addresses/${idNum}`)
        if (!cancelled) setAddress(data)
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Ошибка загрузки')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    
    void load()
    return () => {
      cancelled = true
    }
  }, [validId, idNum])
  
  return (
    <DetailPageShell
      title={`Адрес${address ? ` #${address.id}` : ''}`}
      backHref="/reference/addresses"
      backLabel="← К списку адресов"
      loading={loading}
      error={error}
    >
      {!loading && !error && address ? (
        <dl className="entity-dl">
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">ID</dt>
            <dd className="entity-dl__dd">{address.id}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">Полный адрес</dt>
            <dd className="entity-dl__dd">{address.full_address}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">Краткий</dt>
            <dd className="entity-dl__dd">{address.short_address}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">С индексом</dt>
            <dd className="entity-dl__dd">{address.full_address_with_postal_code}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">Регион</dt>
            <dd className="entity-dl__dd">{address.region}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">Город</dt>
            <dd className="entity-dl__dd">{address.city}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">Улица</dt>
            <dd className="entity-dl__dd">{address.street}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">Дом</dt>
            <dd className="entity-dl__dd">{address.house}</dd>
          </div>
          {address.building ? (
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Корпус</dt>
              <dd className="entity-dl__dd">{address.building}</dd>
            </div>
          ) : null}
          {address.structure ? (
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Строение</dt>
              <dd className="entity-dl__dd">{address.structure}</dd>
            </div>
          ) : null}
          {address.flat ? (
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Квартира</dt>
              <dd className="entity-dl__dd">{address.flat}</dd>
            </div>
          ) : null}
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">Индекс</dt>
            <dd className="entity-dl__dd">{address.postal_code ?? '—'}</dd>
          </div>
          {address.fias_id ? (
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">ФИАС ID</dt>
              <dd className="entity-dl__dd">
                <code>{address.fias_id}</code>
              </dd>
            </div>
          ) : null}
          {address.latitude != null ? (
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Широта</dt>
              <dd className="entity-dl__dd">{address.latitude}</dd>
            </div>
          ) : null}
          {address.longitude != null ? (
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Долгота</dt>
              <dd className="entity-dl__dd">{address.longitude}</dd>
            </div>
          ) : null}
          {address.delivery_zone?.name ? (
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Зона доставки</dt>
              <dd className="entity-dl__dd">{address.delivery_zone.name}</dd>
            </div>
          ) : address.zone_name ? (
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Зона доставки</dt>
              <dd className="entity-dl__dd">{address.zone_name}</dd>
            </div>
          ) : address.delivery_zone_id != null ? (
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Зона доставки (ID)</dt>
              <dd className="entity-dl__dd">{address.delivery_zone_id}</dd>
            </div>
          ) : null}
          {address.source_raw ? (
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Исходная строка</dt>
              <dd className="entity-dl__dd">{address.source_raw}</dd>
            </div>
          ) : null}
          {address.created_at ? (
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Создан</dt>
              <dd className="entity-dl__dd">{formatDt(address.created_at)}</dd>
            </div>
          ) : null}
          {address.updated_at ? (
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Обновлён</dt>
              <dd className="entity-dl__dd">{formatDt(address.updated_at)}</dd>
            </div>
          ) : null}
        </dl>
      ) : null}
    </DetailPageShell>
  )
}
