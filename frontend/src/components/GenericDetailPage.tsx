import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { DetailPageShell } from './DetailPageShell'
import { apiFetch } from '../lib/http'
import { formatDt } from '../lib/formatDt'

type Props = {
  title: string
  apiUrl: string
  backHref: string
  backLabel: string
  fields: {
    key: string
    label: string
    type?: 'text' | 'number' | 'bool' | 'date' | 'datetime'
  }[]
}

export function GenericDetailPage({ title, apiUrl, backHref, backLabel, fields }: Props) {
  const { id } = useParams<{ id: string }>()
  const [data, setData] = useState<Record<string, unknown> | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    ;(async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await apiFetch(`${apiUrl}/${id}`)
        if (res.status === 404) {
          setError('Не найдено')
          return
        }
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = await res.json()
        setData(data)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Ошибка загрузки')
      } finally {
        setLoading(false)
      }
    })()
  }, [apiUrl, id])

  function formatValue(field: Props['fields'][number], value: unknown): string {
    if (value == null) return '—'
    
    switch (field.type) {
      case 'bool':
        return value ? 'Да' : 'Нет'
      case 'date':
        return formatDt(String(value))
      case 'datetime':
        return formatDt(String(value))
      case 'number':
        return String(value)
      default:
        return String(value)
    }
  }

  return (
    <DetailPageShell
      title={`${title}${data?.id ? ` #${data.id}` : ''}`}
      backHref={backHref}
      backLabel={backLabel}
      loading={loading}
      error={error}
    >
      {!loading && !error && data ? (
        <dl className="entity-dl">
          {fields.map((field) => (
            <div key={field.key} className="entity-dl__row">
              <dt className="entity-dl__dt">{field.label}</dt>
              <dd className="entity-dl__dd">{formatValue(field, data[field.key])}</dd>
            </div>
          ))}
        </dl>
      ) : null}
    </DetailPageShell>
  )
}
