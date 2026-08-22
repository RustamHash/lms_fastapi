import { HubPage } from '../components/HubPage'

export function DocumentsHubPage() {
  return (
    <HubPage
      title="Документы"
      subtitle="Документы склада"
      breadcrumbs={[{ label: 'Главная', to: '/' }, { label: 'Документы' }]}
      sections={[
        {
          title: 'Документы',
          icon: '📄',
          items: [
            { to: '/documents', label: 'Все документы', description: 'Все документы', icon: '📋' },
            { to: '/documents?document_type=receiving', label: 'Приход', description: 'Приходные документы', icon: '📥' },
            { to: '/documents?document_type=shipping', label: 'Расход', description: 'Расходные документы', icon: '📤' },
          ],
        },
        {
          title: 'Строки документов',
          icon: '📝',
          items: [
            { to: '/documents', label: 'Строки прихода', description: 'Строки приходных документов', icon: '📥' },
            { to: '/documents', label: 'Строки расхода', description: 'Строки расходных документов', icon: '📤' },
          ],
        },
      ]}
    />
  )
}
