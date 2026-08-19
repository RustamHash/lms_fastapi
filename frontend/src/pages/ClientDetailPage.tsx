import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { DetailPageShell } from '../components/DetailPageShell'
import { apiFetch } from '../lib/http'

type Client = {
  id: number
  depositor_id: number
  external_id: string
  name: string
  legal_name: string
  inn: string
  kpp: string
  is_edo: boolean
  is_deleted: boolean
  is_active: boolean
}

export function ClientDetailPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const canEdit = user?.permissions?.all === true
  const { clientId } = useParams<{ clientId: string }>()
  const [client, setClient] = useState<Client | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!clientId) return
    ;(async () => {
      setLoading(true)
      try {
        const res = await apiFetch(`/api/v1/parties/clients/${clientId}`)
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        setClient(await res.json())
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Ошибка')
      } finally {
        setLoading(false)
      }
    })()
  }, [clientId])

  return (
    <DetailPageShell
      title={client ? client.name : 'Клиент'}
      breadcrumbs={[
        { label: 'Справочники', to: '/references' },
        { label: 'Клиенты', to: '/reference/clients' },
        { label: client ? `#${client.id}` : '' },
      ]}
      loading={loading}
      error={error}
      canEdit={canEdit}
      onEdit={() => navigate('edit')}
    >
      {client ? (
        <dl className="entity-dl">
          <div className="entity-dl__row"><dt>ID</dt><dd>{client.id}</dd></div>
          <div className="entity-dl__row"><dt>Внешний код</dt><dd>{client.external_id}</dd></div>
          <div className="entity-dl__row"><dt>Наименование</dt><dd>{client.name}</dd></div>
          <div className="entity-dl__row"><dt>Полное</dt><dd>{client.legal_name}</dd></div>
          <div className="entity-dl__row"><dt>ИНН</dt><dd>{client.inn}</dd></div>
          <div className="entity-dl__row"><dt>КПП</dt><dd>{client.kpp}</dd></div>
          <div className="entity-dl__row"><dt>ЭДО</dt><dd>{client.is_edo ? 'Да' : 'Нет'}</dd></div>
        </dl>
      ) : null}
    </DetailPageShell>
  )
}
