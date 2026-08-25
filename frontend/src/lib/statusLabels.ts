export const STATUS_LABELS: Record<string, string> = {
  new: 'Новый',
  created: 'Создан',
  document_created: 'Документ создан',
  task_created: 'Задание создано',
  in_progress: 'В работе',
  completed: 'Завершён',
  completed_with_deviations: 'С отклонениями',
  cancelled: 'Отменён',
  shipped: 'Отгружен',
  delivered: 'Доставлен',
  assigned: 'Назначена',
  in_transit: 'В пути',
  failed: 'Ошибка',
  starting: 'Запуск',
  processing: 'Обработка',
  planned: 'Запланирован',
  active: 'Активен',
  pending: 'Ожидает',
  draft: 'Черновик',
}

export function getStatusLabel(status: string | null | undefined): string {
  if (!status) return '—'
  return STATUS_LABELS[status] ?? status
}

const DOCUMENT_TYPES: Record<string, string> = {
  receipt: 'Приходная накладная',
  receiving: 'Приход',
  shipping: 'Расход',
  shipment: 'Отгрузка',
  movement: 'Перемещение',
  inventory: 'Инвентаризация',
  adjustment: 'Корректировка',
  write_off: 'Списание',
}

const DOCUMENT_STATUSES: Record<string, string> = {
  draft: 'Черновик',
  created: 'Создан',
  task_created: 'Задание создано',
  in_progress: 'В работе',
  completed: 'Завершён',
  processed: 'Обработан',
  cancelled: 'Отменён',
}

const TASK_TYPES: Record<string, string> = {
  picking: 'Отбор',
  receiving: 'Приёмка',
  putaway: 'Размещение',
  shipping: 'Отгрузка',
  movement: 'Перемещение',
}

export function getDocumentTypeLabel(type: string): string {
  return DOCUMENT_TYPES[type] ?? type
}

export function getDocumentStatusLabel(status: string): string {
  return DOCUMENT_STATUSES[status] ?? getStatusLabel(status)
}

export function getTaskTypeLabel(type: string): string {
  return TASK_TYPES[type] ?? type
}
