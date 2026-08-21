import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { DetailPageShell } from '../components/DetailPageShell'
import { apiClient } from '../lib/apiClient'

type Tariff = {
  id: number
  document_id: number
  service_group: string
  name: string
  description: string
  unit: string
  price: string
  is_deleted: boolean
  is_active: boolean
}

export function TariffDetailPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const canEdit = user?.permissions?.all === true
  const { tariffId } = useParams<{ tariffId: string }>()
  const [tariff, setTariff] = useState<Tariff | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!tariffId) return
    ;(async () => {
      setLoading(true)
      try {
        const data = await apiClient.get<Tariff>(`/api/v1/parties/tariffs/${tariffId}`)
        setTariff(data)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Ошибка')
      } finally {
        setLoading(false)
      }
    })()
  }, [tariffId])

  return (
    <DetailPageShell
      title={tariff ? tariff.name : 'Тариф'}
      breadcrumbs={[
        { label: 'Справочники', to: '/references' },
        { label: 'Тарифы', to: '/reference/tariffs' },
        { label: tariff ? `#${tariff.id}` : '' },
      ]}
      loading={loading}
      error={error}
      canEdit={canEdit}
      onEdit={() => navigate('edit')}
    >
      {tariff ? (
        <dl className="entity-dl">
          <div className="entity-dl__row"><dt>ID</dt><dd>{tariff.id}</dd></div>
          <div className="entity-dl__row"><dt>Название</dt><dd>{tariff.name}</dd></div>
          <div className="entity-dl__row"><dt>Группа</dt><dd>{tariff.service_group}</dd></div>
          <div className="entity-dl__row"><dt>Единица</dt><dd>{tariff.unit}</dd></div>
          <div className="entity-dl__row"><dt>Цена</dt><dd>{tariff.price}</dd></div>
          <div className="entity-dl__row"><dt>Описание</dt><dd>{tariff.description}</dd></div>
        </dl>
      ) : null}
    </DetailPageShell>
  )
}
