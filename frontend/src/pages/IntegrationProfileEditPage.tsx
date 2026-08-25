import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { apiClient } from '../lib/apiClient'
import {
  buildConfig,
  emptyFtpForm,
  FTP_PATH_FIELDS,
  ftpFromConfig,
  type FtpFields,
} from '../features/integration-profiles/ftpConfig'

type Profile = {
  id: number
  name: string
  depositor_id: number
  source_type: string
  config: Record<string, unknown>
  is_active?: boolean
}

export function IntegrationProfileEditPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: '',
    depositor_id: '',
    source_type: 'zln',
    ...emptyFtpForm(),
  })
  const [previousConfig, setPreviousConfig] = useState<Record<string, unknown>>({})
  const [depositors, setDepositors] = useState<{ id: number; code: string }[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    ;(async () => {
      setLoading(true)
      try {
        const [profile, depositorRows] = await Promise.all([
          apiClient.get<Profile>(`/api/v1/integrations/profiles/${id}`),
          apiClient.get<{ id: number; code: string }[]>('/api/v1/depositors'),
        ])
        const ftp = ftpFromConfig(profile.config)
        setPreviousConfig(profile.config || {})
        setForm({
          name: profile.name,
          depositor_id: String(profile.depositor_id),
          source_type: profile.source_type,
          ...ftp,
        })
        setDepositors(depositorRows)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Ошибка загрузки')
      } finally {
        setLoading(false)
      }
    })()
  }, [id])

  function patchFtp<K extends keyof FtpFields>(key: K, value: FtpFields[K]) {
    setForm((p) => ({ ...p, [key]: value }))
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      const saved = await apiClient.patch<Profile>(`/api/v1/integrations/profiles/${id}`, {
        name: form.name,
        depositor_id: Number(form.depositor_id),
        source_type: form.source_type,
        config: buildConfig(
          {
            host: form.host,
            username: form.username,
            password: form.password,
            in_path: form.in_path,
            out_path: form.out_path,
            print_path: form.print_path,
            archive_path: form.archive_path,
            error_path: form.error_path,
          },
          previousConfig,
        ),
      })
      navigate(`/integrations/profiles/${id}`, { state: { profile: saved } })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка сохранения')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <p>Загрузка...</p>

  return (
    <section className="app-card app-card--wide">
      <h1 className="page-title">Редактирование профиля</h1>
      <form onSubmit={onSubmit} className="wh-form wh-form--wide">
        <label>
          Название *
          <input
            value={form.name}
            onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
            required
          />
        </label>
        <label>
          Поклажедатель
          <select
            value={form.depositor_id}
            onChange={(e) => setForm((p) => ({ ...p, depositor_id: e.target.value }))}
            required
          >
            <option value="">— выберите —</option>
            {depositors.map((d) => (
              <option key={d.id} value={d.id}>
                {d.code}
              </option>
            ))}
          </select>
        </label>
        <label>
          Тип источника
          <select
            value={form.source_type}
            onChange={(e) => setForm((p) => ({ ...p, source_type: e.target.value }))}
          >
            <option value="zln">ZLN</option>
            <option value="manual">Ручной</option>
          </select>
        </label>
        <label>
          FTP хост
          <input value={form.host} onChange={(e) => patchFtp('host', e.target.value)} />
        </label>
        <label>
          FTP логин
          <input
            value={form.username}
            onChange={(e) => patchFtp('username', e.target.value)}
          />
        </label>
        <label>
          FTP пароль
          <input
            type="password"
            value={form.password}
            onChange={(e) => patchFtp('password', e.target.value)}
          />
        </label>
        {FTP_PATH_FIELDS.map((field) => (
          <label key={field.key}>
            {field.label}
            <input
              value={form[field.key]}
              placeholder={field.hint}
              onChange={(e) => patchFtp(field.key, e.target.value)}
            />
            <span className="wh-form__hint">{field.hint}</span>
          </label>
        ))}
        {error ? <p className="wh-form__err">{error}</p> : null}
        <div className="wh-form__actions">
          <button type="submit" disabled={saving}>
            {saving ? 'Сохранение...' : 'Сохранить'}
          </button>
          <button type="button" onClick={() => navigate(`/integrations/profiles/${id}`)}>
            Отмена
          </button>
        </div>
      </form>
    </section>
  )
}
