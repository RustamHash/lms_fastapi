import { useEffect, useState } from 'react'
import { useLocation, useParams } from 'react-router-dom'
import { useAuth, hasPermission } from '../auth/AuthContext'
import { DetailPageShell } from '../components/DetailPageShell'
import { apiClient } from '../lib/apiClient'
import {
  ftpFromConfig,
  restConfigWithoutFtp,
} from '../features/integration-profiles/ftpConfig'

type Profile = {
  id: number
  depositor_id: number
  name: string
  source_type: string
  config: Record<string, unknown>
  is_active: boolean
}

export function IntegrationProfileDetailPage() {
  const { user } = useAuth()
  const canEdit = hasPermission(user, 'integrations', 'update')
  const { id } = useParams<{ id: string }>()
  const location = useLocation()
  const saved = (location.state as { profile?: Profile } | null)?.profile
  const [profile, setProfile] = useState<Profile | null>(
    saved && String(saved.id) === id ? saved : null,
  )
  const [loading, setLoading] = useState(!profile)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    const fromSave = (location.state as { profile?: Profile } | null)?.profile
    if (fromSave && String(fromSave.id) === id) {
      setProfile(fromSave)
      setLoading(false)
    }
    let cancelled = false
    ;(async () => {
      if (!fromSave) {
        setLoading(true)
      }
      setError(null)
      try {
        const data = await apiClient.get<Profile>(`/api/v1/integrations/profiles/${id}`)
        if (!cancelled) setProfile(data)
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Ошибка загрузки')
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [id, location.key, location.state])

  const ftp = ftpFromConfig(profile?.config)
  const extra = restConfigWithoutFtp(profile?.config)
  const hasExtra = Object.keys(extra).length > 0

  return (
    <DetailPageShell
      title={profile ? profile.name : 'Профиль интеграции'}
      breadcrumbs={[
        { label: 'Интеграции', to: '/integrations' },
        { label: 'Профили', to: '/integrations/profiles' },
        { label: profile ? `#${profile.id}` : '' },
      ]}
      loading={loading}
      error={error}
      canEdit={canEdit}
      editPath={profile ? `/integrations/profiles/${profile.id}/edit` : undefined}
    >
      {profile ? (
        <dl className="entity-dl">
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">ID</dt>
            <dd className="entity-dl__dd">{profile.id}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">Название</dt>
            <dd className="entity-dl__dd">{profile.name}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">Поклажедатель</dt>
            <dd className="entity-dl__dd">#{profile.depositor_id}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">Тип источника</dt>
            <dd className="entity-dl__dd">{profile.source_type}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">Активен</dt>
            <dd className="entity-dl__dd">{profile.is_active ? 'Да' : 'Нет'}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">FTP хост</dt>
            <dd className="entity-dl__dd">{ftp.host || '—'}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">FTP логин</dt>
            <dd className="entity-dl__dd">{ftp.username || '—'}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">FTP пароль</dt>
            <dd className="entity-dl__dd">{ftp.password || '—'}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">Входящие</dt>
            <dd className="entity-dl__dd">{ftp.in_path || '—'}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">Исходящие</dt>
            <dd className="entity-dl__dd">{ftp.out_path || '—'}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">Печатные формы</dt>
            <dd className="entity-dl__dd">{ftp.print_path || '—'}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">Архив</dt>
            <dd className="entity-dl__dd">{ftp.archive_path || '—'}</dd>
          </div>
          <div className="entity-dl__row">
            <dt className="entity-dl__dt">Ошибки</dt>
            <dd className="entity-dl__dd">{ftp.error_path || '—'}</dd>
          </div>
          {hasExtra ? (
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Прочие настройки</dt>
              <dd className="entity-dl__dd">
                <pre>{JSON.stringify(extra, null, 2)}</pre>
              </dd>
            </div>
          ) : null}
        </dl>
      ) : null}
    </DetailPageShell>
  )
}
