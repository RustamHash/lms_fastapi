import type { ListPageConfig } from '../entity-system/types'

type TaskRow = {
  id: number
  task_type: string
  document_id: number | null
  assignee_id: number | null
  status: string
}

export const tasksConfig: ListPageConfig<TaskRow> = {
  entityKey: 'tasks',
  title: 'Задания',
  apiUrl: '/api/v1/warehouse/tasks',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'task_type', label: 'Тип задания', type: 'text' },
    { id: 'status', label: 'Статус', type: 'text' },
    { id: 'document_id', label: 'Документ ID', type: 'number' },
    { id: 'assignee_id', label: 'Исполнитель ID', type: 'number' },
  ],
  filters: [
    { 
      id: 'task_type', 
      type: 'select', 
      label: 'Тип задания',
      options: [
        { value: 'receiving', label: 'Приёмка' },
        { value: 'putaway', label: 'Размещение' },
        { value: 'picking', label: 'Отбор' },
        { value: 'shipping', label: 'Отгрузка' },
        { value: 'movement', label: 'Перемещение' },
      ],
    },
    { 
      id: 'status', 
      type: 'select', 
      label: 'Статус',
      options: [
        { value: 'new', label: 'Новое' },
        { value: 'in_progress', label: 'В работе' },
        { value: 'completed', label: 'Завершено' },
        { value: 'completed_with_deviations', label: 'С отклонениями' },
      ],
    },
  ],
  columnOverrides: {
    id: { href: (row) => `/tasks/${row.id}` },
  },
}
