import { Link } from 'react-router-dom'

const FILE_ITEMS = [
  { to: '/files', label: 'Все файлы', description: 'Список всех файлов' },
  { to: '/files', label: 'Загрузить', description: 'Загрузка нового файла' },
]

export function FilesHubPage() {
  return (
    <section className="app-card app-card--wide">
      <h1 className="page-title">Файлы</h1>
      <p className="app-intro">Файловый менеджер</p>

      <div className="ref-groups">
        <section className="ref-group">
          <h2 className="ref-group__title">Файлы</h2>
          <div className="ref-group__cards">
            {FILE_ITEMS.map((item) => (
              <Link key={item.label} to={item.to} className="ref-card">
                <span className="ref-card__title">{item.label}</span>
                <span className="ref-card__desc">{item.description}</span>
              </Link>
            ))}
          </div>
        </section>
      </div>
    </section>
  )
}
