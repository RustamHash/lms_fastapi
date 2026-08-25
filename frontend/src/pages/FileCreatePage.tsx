import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../lib/apiClient'

export function FileCreatePage() {
  const navigate = useNavigate()
  const [file, setFile] = useState<File | null>(null)
  const [fileType, setFileType] = useState('document_scan')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!file) return
    setSaving(true)
    setError(null)
    try {
      const form = new FormData()
      form.append('file', file)
      form.append('file_type', fileType)
      const created = await apiClient.postForm<{ id: number }>(
        `/api/v1/files/upload?file_type=${encodeURIComponent(fileType)}`,
        form,
      )
      navigate(`/files/${created.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка')
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="app-card app-card--wide">
      <h1 className="page-title">Загрузить файл</h1>
      <form onSubmit={handleSubmit} className="wh-form">
        <label>
          Файл *
          <input
            type="file"
            required
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </label>
        <label>
          Тип
          <input value={fileType} onChange={(e) => setFileType(e.target.value)} />
        </label>
        {error ? <p className="wh-form__err">{error}</p> : null}
        <div className="wh-form__actions">
          <button type="submit" className="tb tb--create" disabled={saving || !file}>
            {saving ? 'Загрузка...' : 'Загрузить'}
          </button>
          <button type="button" className="tb tb--reset" onClick={() => navigate('/files')}>
            Отмена
          </button>
        </div>
      </form>
    </section>
  )
}
