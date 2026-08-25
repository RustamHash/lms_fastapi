import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../lib/apiClient'
import {
  buildConfig,
  emptyFtpForm,
  FTP_PATH_FIELDS,
} from '../features/integration-profiles/ftpConfig'

export function IntegrationProfileCreatePage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: '',
    depositor_id: '',
    source_type: 'zln',
    ...emptyFtpForm(),
  })
  const [depositors, setDepositors] = useState<{ id: number; code: string }[]>([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    ;(async () => {
      const data = await apiClient.get<{ id: number; code: string }[]>('/api/v1/depositors')
      setDepositors(data)
    })()
  }, [])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      const created = await apiClient.post<{ id: number }>('/api/v1/integrations/profiles', {
        name: form.name,
        depositor_id: Number(form.depositor_id),
        source_type: form.source_type,
        config: buildConfig({
          host: form.host,
          username: form.username,
          password: form.password,
          in_path: form.in_path,
          out_path: form.out_path,
          print_path: form.print_path,
          archive_path: form.archive_path,
          error_path: form.error_path,
        }),
      })
      navigate(`/integrations/profiles/${created.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка')
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="app-card app-card--wide">
      <h1 className="page-title">Новый профиль интеграции</h1>
      <form onSubmit={onSubmit} className="wh-form wh-form--wide">
        <label>Название *<input value={form.name} onChange={(e) => setForm((p) => ({...p, name: e.target.value}))} required /></label>
        <label>Поклажедатель
          <select value={form.depositor_id} onChange={(e) => setForm((p) => ({...p, depositor_id: e.target.value}))}>
            <option value="">— выберите —</option>
            {depositors.map((d) => (
              <option key={d.id} value={d.id}>{d.code}</option>
            ))}
          </select>
        </label>
        <label>Тип источника
          <select value={form.source_type} onChange={(e) => setForm((p) => ({...p, source_type: e.target.value}))}>
            <option value="zln">ZLN</option>
            <option value="manual">Ручной</option>
          </select>
        </label>
        <label>FTP хост<input value={form.host} onChange={(e) => setForm((p) => ({...p, host: e.target.value}))} /></label>
        <label>FTP логин<input value={form.username} onChange={(e) => setForm((p) => ({...p, username: e.target.value}))} /></label>
        <label>FTP пароль<input type="password" value={form.password} onChange={(e) => setForm((p) => ({...p, password: e.target.value}))} /></label>
        {FTP_PATH_FIELDS.map((field) => (
          <label key={field.key}>
            {field.label}
            <input
              value={form[field.key]}
              placeholder={field.hint}
              onChange={(e) => setForm((p) => ({ ...p, [field.key]: e.target.value }))}
            />
            <span className="wh-form__hint">{field.hint}</span>
          </label>
        ))}
        {error ? <p className="wh-form__err">{error}</p> : null}
        <div className="wh-form__actions">
          <button type="submit" disabled={saving}>{saving ? 'Создание...' : 'Создать'}</button>
          <button type="button" onClick={() => navigate('/integrations/profiles')}>Отмена</button>
        </div>
      </form>
    </section>
  )
}
