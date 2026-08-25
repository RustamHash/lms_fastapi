import { useEffect, useState, type ReactNode } from 'react'
import { useParams } from 'react-router-dom'
import { DetailPageShell } from '../components/DetailPageShell'
import { apiClient } from '../lib/apiClient'
import { formatDt } from '../lib/formatDt'

type Log = {
  id: number
  task_id: string
  profile_id: number | null
  status: string
  document_type: string | null
  total_rows: number
  processed_rows: number
  success_rows: number
  error_rows: number
  messages: string[]
  errors: string[]
  current_step: string
  order_number: string
  created_at: string
}

export function IntegrationLogDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [log, setLog] = useState<Log | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    let cancelled = false
    ;(async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await apiClient.get<Log>(`/api/v1/integrations/logs/${id}`)
        if (!cancelled) setLog(data)
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Ошибка загрузки')
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [id])

  return (
    <DetailPageShell
      title={log ? `Лог #${log.id}` : 'Лог интеграции'}
      breadcrumbs={[
        { label: 'Интеграции', to: '/integrations' },
        { label: 'Логи', to: '/integrations/logs' },
        { label: log ? `#${log.id}` : '' },
      ]}
      loading={loading}
      error={error}
    >
      {log ? (
        <dl className="entity-dl">
          <Row label="ID">{log.id}</Row>
          <Row label="Задача">{log.task_id}</Row>
          <Row label="Профиль">{log.profile_id ?? '—'}</Row>
          <Row label="Статус">{log.status}</Row>
          <Row label="Тип">{log.document_type || '—'}</Row>
          <Row label="Шаг">{log.current_step || '—'}</Row>
          <Row label="Всего / обработано">{`${log.total_rows} / ${log.processed_rows}`}</Row>
          <Row label="Успешно / ошибок">{`${log.success_rows} / ${log.error_rows}`}</Row>
          <Row label="Создан">{formatDt(log.created_at)}</Row>
          <Row label="Номер">{log.order_number || '—'}</Row>
          <Row label="Сообщения">
            <Lines items={log.messages} empty="нет" />
          </Row>
          <Row label="Ошибки">
            <Lines items={log.errors} empty="нет" />
          </Row>
        </dl>
      ) : null}
    </DetailPageShell>
  )
}

function Row({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="entity-dl__row">
      <dt className="entity-dl__dt">{label}</dt>
      <dd className="entity-dl__dd">{children}</dd>
    </div>
  )
}

function Lines({ items, empty }: { items: string[]; empty: string }) {
  if (!items?.length) return empty
  return (
    <ul>
      {items.map((item, i) => (
        <li key={i}>{item}</li>
      ))}
    </ul>
  )
}
