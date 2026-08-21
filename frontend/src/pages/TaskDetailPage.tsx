import { GenericDetailPage } from '../components/GenericDetailPage'

export function TaskDetailPage() {
  return (
    <GenericDetailPage
      title="Задание"
      apiUrl="/api/v1/warehouse/tasks"
      backHref="/tasks"
      backLabel="← К заданиям"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'task_type', label: 'Тип', type: 'text' as const },
        { key: 'status', label: 'Статус', type: 'text' as const },
        { key: 'document_id', label: 'Документ ID', type: 'number' as const },
        { key: 'assignee_id', label: 'Исполнитель ID', type: 'number' as const },
      ]}
    />
  )
}
