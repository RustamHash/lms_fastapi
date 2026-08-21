import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { DetailPageShell } from '../components/DetailPageShell'
import { apiClient } from '../lib/apiClient'

type Depositor = {
  id: number
  code: string
  legal_entity_id: number
  is_deleted: boolean
  is_active: boolean
}

export function DepositorDetailPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const canEdit = user?.permissions?.all === true
  const { depositorId } = useParams<{ depositorId: string }>()
  const [depositor, setDepositor] = useState<Depositor | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!depositorId) return
    ;(async () => {
      setLoading(true)
      try {
        const data = await apiClient.get<Depositor>(`/api/v1/parties/depositors/${depositorId}`)
        setDepositor(data)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Ошибка')
      } finally {
        setLoading(false)
      }
    })()
  }, [depositorId])

  return (
    <DetailPageShell
      title={depositor ? `Поклажедатель #${depositor.id}` : 'Поклажедатель'}
      breadcrumbs={[
        { label: 'Справочники', to: '/references' },
        { label: 'Поклажедатели', to: '/reference/depositors' },
        { label: depositor ? `#${depositor.id}` : '' },
      ]}
      loading={loading}
      error={error}
      canEdit={canEdit}
      onEdit={() => navigate('edit')}
    >
      {depositor ? (
        <dl className="entity-dl">
          <div className="entity-dl__row"><dt>ID</dt><dd>{depositor.id}</dd></div>
          <div className="entity-dl__row"><dt>Код</dt><dd>{depositor.code}</dd></div>
          <div className="entity-dl__row"><dt>Юрлицо ID</dt><dd>{depositor.legal_entity_id}</dd></div>
          <div className="entity-dl__row"><dt>Удалён</dt><dd>{depositor.is_deleted ? 'Да' : 'Нет'}</dd></div>
        </dl>
      ) : null}
    </DetailPageShell>
  )
}
