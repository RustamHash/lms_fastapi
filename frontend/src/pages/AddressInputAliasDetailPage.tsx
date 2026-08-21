import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { DetailPageShell } from '../components/DetailPageShell'
import { apiClient } from '../lib/apiClient'
import { formatDt } from '../lib/formatDt'

type AddressInputAliasDetail = {
  id: number
  raw_text: string
  hash: string
  normalized_address_id: number
  full_address: string | null
  source: string
  created_at?: string
  updated_at?: string
}

export function AddressInputAliasDetailPage() {
  const { aliasId } = useParams<{ aliasId: string }>()
  const idNum = aliasId ? Number(aliasId) : NaN
  const validId = Number.isInteger(idNum) && idNum > 0
  
  const [alias, setAlias] = useState<AddressInputAliasDetail | null>(null)
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
        const data = await apiClient.get<AddressInputAliasDetail>(`/api/v1/parties/aliases/${idNum}`)
        const data = await res.json() as AddressInputAliasDetail
        if (!cancelled) setAlias(data)
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
      title={`Вариант ввода${alias ? ` #${alias.id}` : ''}`}
      backHref="/reference/address-input-aliases"
      backLabel="← К списку вариантов ввода"
      loading={loading}
      error={error}
    >
      {!loading && !error && alias ? (
        <dl className="entity-dl">
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">ID</dt>
            <dd className="entity-dl__dd">{alias.id}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">Исходная строка</dt>
            <dd className="entity-dl__dd">{alias.raw_text}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">Норм. ключ</dt>
            <dd className="entity-dl__dd">
              <code>{alias.hash}</code>
            </dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">Адрес ID</dt>
            <dd className="entity-dl__dd">{alias.normalized_address_id}</dd>
          </div>
          {alias.full_address ? (
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Адрес</dt>
              <dd className="entity-dl__dd">{alias.full_address}</dd>
            </div>
          ) : null}
          {alias.source ? (
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Источник</dt>
              <dd className="entity-dl__dd">{alias.source}</dd>
            </div>
          ) : null}
          {alias.created_at ? (
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Создан</dt>
              <dd className="entity-dl__dd">{formatDt(alias.created_at)}</dd>
            </div>
          ) : null}
          {alias.updated_at ? (
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Обновлён</dt>
              <dd className="entity-dl__dd">{formatDt(alias.updated_at)}</dd>
            </div>
          ) : null}
        </dl>
      ) : null}
    </DetailPageShell>
  )
}
