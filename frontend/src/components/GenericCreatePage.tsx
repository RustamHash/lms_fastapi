import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../lib/apiClient'
import { resolveCreateForm } from '../features/entity-system/createForms'
import type { CreateField, ListPageConfig } from '../features/entity-system/types'

type Props<Row extends { id: number }> = {
  config: ListPageConfig<Row>
}

function emptyValues(fields: CreateField[]): Record<string, string | boolean> {
  const next: Record<string, string | boolean> = {}
  for (const field of fields) {
    next[field.key] = field.type === 'bool' ? false : ''
  }
  return next
}

function buildPayload(fields: CreateField[], values: Record<string, string | boolean>): Record<string, unknown> {
  const body: Record<string, unknown> = {}
  for (const field of fields) {
    const raw = values[field.key]
    if (field.type === 'bool') {
      body[field.key] = Boolean(raw)
      continue
    }
    const text = String(raw ?? '').trim()
    if (text === '') {
      if (field.required) body[field.key] = text
      continue
    }
    if (field.type === 'number') {
      const n = Number(text)
      if (!Number.isNaN(n)) body[field.key] = n
      continue
    }
    body[field.key] = text
  }
  return body
}

export function GenericCreatePage<Row extends { id: number }>({ config }: Props<Row>) {
  const navigate = useNavigate()
  const form = resolveCreateForm(config)
  const [values, setValues] = useState<Record<string, string | boolean>>(() =>
    form ? emptyValues(form.fields) : {},
  )
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const listPath = config.listPath ?? '/'

  if (!form) {
    return (
      <section className="app-card app-card--wide">
        <h1 className="page-title">Создание недоступно</h1>
        <p>Для «{config.title}» нет формы создания.</p>
        <button type="button" className="tb tb--reset" onClick={() => navigate(listPath)}>
          К списку
        </button>
      </section>
    )
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form) return
    setSaving(true)
    setError(null)
    try {
      const created = await apiClient.post<{ id: number }>(form.apiUrl, buildPayload(form.fields, values))
      navigate(`${listPath}/${created.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка')
    } finally {
      setSaving(false)
    }
  }

  function setField(key: string, value: string | boolean) {
    setValues((prev) => ({ ...prev, [key]: value }))
  }

  return (
    <section className="app-card app-card--wide">
      <h1 className="page-title">Новый: {config.title}</h1>
      <form onSubmit={handleSubmit} className="wh-form">
        {form.fields.map((field) => (
          <label key={field.key}>
            {field.label}
            {field.required ? ' *' : ''}
            {field.type === 'bool' ? (
              <input
                type="checkbox"
                checked={Boolean(values[field.key])}
                onChange={(e) => setField(field.key, e.target.checked)}
              />
            ) : field.type === 'textarea' ? (
              <textarea
                value={String(values[field.key] ?? '')}
                onChange={(e) => setField(field.key, e.target.value)}
                required={field.required}
                rows={3}
              />
            ) : (
              <input
                type={
                  field.type === 'number'
                    ? 'number'
                    : field.type === 'date'
                      ? 'date'
                      : field.type === 'password'
                        ? 'password'
                        : 'text'
                }
                value={String(values[field.key] ?? '')}
                onChange={(e) => setField(field.key, e.target.value)}
                required={field.required}
                autoFocus={field === form.fields[0]}
              />
            )}
          </label>
        ))}
        {error ? <p className="wh-form__err">{error}</p> : null}
        <div className="wh-form__actions">
          <button type="submit" className="tb tb--create" disabled={saving}>
            {saving ? 'Создание...' : 'Создать'}
          </button>
          <button type="button" className="tb tb--reset" onClick={() => navigate(listPath)}>
            Отмена
          </button>
        </div>
      </form>
    </section>
  )
}
