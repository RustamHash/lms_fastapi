import type { ListPageConfig } from '../entity-list/types'

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
    { id: 'task_type', type: 'text', label: 'Тип задания' },
    { id: 'status', type: 'text', label: 'Статус' },
  ],
  columnOverrides: {
    id: { href: (row) => `/warehouse/tasks/${row.id}` },
  },
}
