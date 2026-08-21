import type { ListPageConfig } from '../entity-system/types'

type NotificationRow = {
  id: number
  user_id: number
  title: string
  text: string
  notification_type: string
  status: string
  link: string
  sent_at: string | null
  read_at: string | null
}

export const notificationsConfig: ListPageConfig<NotificationRow> = {
  entityKey: 'notifications',
  title: 'Уведомления',
  apiUrl: '/api/v1/notifications',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'title', label: 'Заголовок', type: 'text' },
    { id: 'text', label: 'Сообщение', type: 'text' },
    { id: 'notification_type', label: 'Тип', type: 'text' },
    { id: 'status', label: 'Статус', type: 'text' },
    { id: 'read_at', label: 'Прочитано', type: 'date' },
  ],
  filters: [
    { id: 'title', type: 'text', label: 'Заголовок' },
    { id: 'status', type: 'text', label: 'Статус' },
  ],
}
