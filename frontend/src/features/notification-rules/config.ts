import type { ListPageConfig } from '../entity-system/types'

type NotificationRuleRow = {
  id: number
  event_type: string
  channel: string
  recipient_type: string
  recipient_id: number | null
  role_code: string | null
  is_active: boolean
}

export const notificationRulesConfig: ListPageConfig<NotificationRuleRow> = {
  entityKey: 'notification_rules',
  title: 'Правила уведомлений',
  apiUrl: '/api/v1/notification-rules',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'event_type', label: 'Событие', type: 'text' },
    { id: 'channel', label: 'Канал', type: 'text' },
    { id: 'recipient_type', label: 'Тип получателя', type: 'text' },
    { id: 'recipient_id', label: 'Получатель ID', type: 'number' },
    { id: 'role_code', label: 'Роль', type: 'text' },
    { id: 'is_active', label: 'Активно', type: 'bool' },
  ],
  filters: [
    { id: 'event_type', type: 'text', label: 'Событие' },
    { id: 'channel', type: 'text', label: 'Канал' },
    { id: 'recipient_type', type: 'text', label: 'Тип получателя' },
  ],

  columnOverrides: {
    id: { href: (row) => `/reference/notification-rules/${row.id}` },
  },
}