import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { DetailPageShell } from '../components/DetailPageShell'
import { apiClient } from '../lib/apiClient'

type LegalEntity = {
  id: number
  name: string
  legal_name: string
  inn: string
  kpp: string
  ogrn: string
  phone: string
  email: string
  is_deleted: boolean
  is_active: boolean
}

export function LegalEntityDetailPage() {
  
  const { user } = useAuth()
  const canEdit = user?.permissions?.all === true
  const { entityId } = useParams<{ entityId: string }>()
  const [entity, setEntity] = useState<LegalEntity | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!entityId) return
    ;(async () => {
      setLoading(true)
      try {
        const data = await apiClient.get<LegalEntity>(`/api/v1/parties/legal-entities/${entityId}`)
        setEntity(data)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Ошибка')
      } finally {
        setLoading(false)
      }
    })()
  }, [entityId])

  return (
    <DetailPageShell
      title={entity ? entity.name : 'Юрлицо'}
      breadcrumbs={[
        { label: 'Справочники', to: '/references' },
        { label: 'Юрлица', to: '/reference/legal-entities' },
        { label: entity ? `#${entity.id}` : '' },
      ]}
      loading={loading}
      error={error}
      canEdit={canEdit}
      editPath={entity ? `/reference/legal-entities/${entity.id}/edit` : undefined}
    >
      {entity ? (
        <dl className="entity-dl">
          <div className="entity-dl__row"><dt>ID</dt><dd>{entity.id}</dd></div>
          <div className="entity-dl__row"><dt>Наименование</dt><dd>{entity.name}</dd></div>
          <div className="entity-dl__row"><dt>Полное</dt><dd>{entity.legal_name}</dd></div>
          <div className="entity-dl__row"><dt>ИНН</dt><dd>{entity.inn}</dd></div>
          <div className="entity-dl__row"><dt>КПП</dt><dd>{entity.kpp}</dd></div>
          <div className="entity-dl__row"><dt>ОГРН</dt><dd>{entity.ogrn}</dd></div>
          <div className="entity-dl__row"><dt>Телефон</dt><dd>{entity.phone}</dd></div>
          <div className="entity-dl__row"><dt>Email</dt><dd>{entity.email}</dd></div>
          <div className="entity-dl__row"><dt>Удалено</dt><dd>{entity.is_deleted ? 'Да' : 'Нет'}</dd></div>
        </dl>
      ) : null}
    </DetailPageShell>
  )
}
