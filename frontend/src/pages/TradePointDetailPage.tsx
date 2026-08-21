import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { DetailPageShell } from '../components/DetailPageShell'
import { apiClient } from '../lib/apiClient'

type TradePoint = {
  id: number
  client_id: number
  address_id: number
  name: string
  is_deleted: boolean
  is_active: boolean
}

export function TradePointDetailPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const canEdit = user?.permissions?.all === true
  const { tpId } = useParams<{ tpId: string }>()
  const [tp, setTp] = useState<TradePoint | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!tpId) return
    ;(async () => {
      setLoading(true)
      try {
        const data = await apiClient.get<TradePoint>(`/api/v1/parties/trade-points/${tpId}`)
        setTp(data)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Ошибка')
      } finally {
        setLoading(false)
      }
    })()
  }, [tpId])

  return (
    <DetailPageShell
      title={tp ? tp.name || `Точка #${tp.id}` : 'Торговая точка'}
      breadcrumbs={[
        { label: 'Справочники', to: '/references' },
        { label: 'Торговые точки', to: '/reference/trade-points' },
        { label: tp ? `#${tp.id}` : '' },
      ]}
      loading={loading}
      error={error}
      canEdit={canEdit}
      onEdit={() => navigate('edit')}
    >
      {tp ? (
        <dl className="entity-dl">
          <div className="entity-dl__row"><dt>ID</dt><dd>{tp.id}</dd></div>
          <div className="entity-dl__row"><dt>Название</dt><dd>{tp.name || '—'}</dd></div>
          <div className="entity-dl__row"><dt>Клиент ID</dt><dd>{tp.client_id}</dd></div>
          <div className="entity-dl__row"><dt>Адрес ID</dt><dd>{tp.address_id}</dd></div>
        </dl>
      ) : null}
    </DetailPageShell>
  )
}
