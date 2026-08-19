import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-list/EntityListPage'
import { tasksConfig } from '../features/tasks/config'

export function TasksPage() {
  const navigate = useNavigate()
  return (
    <EntityListPage
      config={tasksConfig}
      onBack={() => navigate(-1)}
      breadcrumbs={[
        { label: 'Склад', to: '/' },
        { label: 'Задания' },
      ]}
    />
  )
}
