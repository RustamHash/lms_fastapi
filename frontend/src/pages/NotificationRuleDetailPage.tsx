import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { DetailPageShell } from '../components/DetailPageShell'
import { apiFetch } from '../lib/http'
import { formatDt } from '../lib/formatDt'

type NotificationRule = {
  id: number
  event_type: string
  channel: string
  recipient_type: string
  recipient_id: number | null
  role_code: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export function NotificationRuleDetailPage() {
  const { ruleId } = useParams<{ ruleId: string }>()
  const [rule, setRule] = useState<NotificationRule | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!ruleId) return
    ;(async () => {
      setLoading(true)
      try {
        const res = await apiFetch(`/api/v1/notification-rules/${ruleId}`)
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        setRule(await res.json())
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Ошибка')
      } finally {
        setLoading(false)
      }
    })()
  }, [ruleId])

  return (
    <DetailPageShell
      title={rule ? `Правило #${rule.id}` : 'Правило уведомления'}
      backHref="/notification-rules"
      backLabel="← К правилам"
      loading={loading}
      error={error}
    >
      {rule ? (
        <dl className="entity-dl">
          <div className="entity-dl__row"><dt>ID</dt><dd>{rule.id}</dd></div>
          <div className="entity-dl__row"><dt>Событие</dt><dd>{rule.event_type}</dd></div>
          <div className="entity-dl__row"><dt>Канал</dt><dd>{rule.channel}</dd></div>
          <div className="entity-dl__row"><dt>Тип получателя</dt><dd>{rule.recipient_type}</dd></div>
          <div className="entity-dl__row"><dt>Получатель ID</dt><dd>{rule.recipient_id ?? '—'}</dd></div>
          <div className="entity-dl__row"><dt>Роль</dt><dd>{rule.role_code ?? '—'}</dd></div>
          <div className="entity-dl__row"><dt>Активно</dt><dd>{rule.is_active ? 'Да' : 'Нет'}</dd></div>
          <div className="entity-dl__row"><dt>Создано</dt><dd>{formatDt(rule.created_at)}</dd></div>
          <div className="entity-dl__row"><dt>Обновлено</dt><dd>{formatDt(rule.updated_at)}</dd></div>
        </dl>
      ) : null}
    </DetailPageShell>
  )
}
