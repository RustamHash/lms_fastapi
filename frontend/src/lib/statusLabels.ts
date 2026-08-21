export const STATUS_LABELS: Record<string, string> = {
  'created': 'Создан',
  'document_created': 'Документ создан',
  'shipped': 'Отгружен',
  'delivered': 'Доставлен',
  'completed': 'Завершён',
  'cancelled': 'Отменён',
  'new': 'Новый',
  'in_progress': 'В работе',
  'completed_with_deviations': 'С отклонениями',
  'starting': 'Запуск',
  'processing': 'Обработка',
  'failed': 'Ошибка',
  'planned': 'Запланирован',
  'active': 'Активен',
  'pending': 'Ожидает',
}

export function getStatusLabel(status: string | null | undefined): string {
  if (!status) return '—'
  return STATUS_LABELS[status] ?? status
}

const DOCUMENT_TYPES: Record<string, string> = {
  'receiving': 'Приход',
  'shipping': 'Расход',
  'shipment': 'Отгрузка',
  'movement': 'Перемещение',
  'inventory': 'Инвентаризация',
  'write_off': 'Списание',
}

const DOCUMENT_STATUSES: Record<string, string> = {
  'draft': 'Черновик',
  'created': 'Создан',
  'in_progress': 'В работе',
  'completed': 'Завершён',
  'processed': 'Обработан',
  'cancelled': 'Отменён',
}

const TASK_TYPES: Record<string, string> = {
  'picking': 'Отбор',
  'receiving': 'Приёмка',
  'putaway': 'Размещение',
  'shipping': 'Отгрузка',
  'movement': 'Перемещение',
}

export function getDocumentTypeLabel(type: string): string {
  return DOCUMENT_TYPES[type] ?? type
}

export function getDocumentStatusLabel(status: string): string {
  return DOCUMENT_STATUSES[status] ?? status
}

export function getTaskTypeLabel(type: string): string {
  return TASK_TYPES[type] ?? type
}
