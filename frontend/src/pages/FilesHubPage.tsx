import { HubPage } from '../components/HubPage'

export function FilesHubPage() {
  return (
    <HubPage
      title="Файлы"
      subtitle="Файловый менеджер"
      breadcrumbs={[{ label: 'Главная', to: '/' }, { label: 'Файлы' }]}
      sections={[
        {
          title: 'Файлы',
          icon: '📁',
          items: [
            { to: '/files', label: 'Все файлы', description: 'Список всех файлов', icon: '📋' },
            { to: '/files', label: 'Загрузить', description: 'Загрузка нового файла', icon: '⬆️' },
          ],
        },
      ]}
    />
  )
}
