import { Link } from 'react-router-dom'

type DocumentGroup = {
  title: string
  items: {
    to: string
    label: string
    description: string
  }[]
}

const DOCUMENT_GROUPS: DocumentGroup[] = [
  {
    title: 'Документы',
    items: [
      { to: '/documents', label: 'Все документы', description: 'Все документы' },
      { to: '/documents?document_type=receiving', label: 'Приход', description: 'Приходные документы' },
      { to: '/documents?document_type=shipping', label: 'Расход', description: 'Расходные документы' },
    ],
  },
  {
    title: 'Строки документов',
    items: [
      { to: '/documents', label: 'Строки прихода', description: 'Строки приходных документов' },
      { to: '/documents', label: 'Строки расхода', description: 'Строки расходных документов' },
    ],
  },
]

export function DocumentsHubPage() {
  return (
    <section className="app-card app-card--wide">
      <h1 className="page-title">Документы</h1>
      <p className="app-intro">Документы склада</p>

      <div className="ref-groups">
        {DOCUMENT_GROUPS.map((group) => (
          <section key={group.title} className="ref-group">
            <h2 className="ref-group__title">{group.title}</h2>
            <div className="ref-group__cards">
              {group.items.map((item) => (
                <Link key={item.to + item.label} to={item.to} className="ref-card">
                  <span className="ref-card__title">{item.label}</span>
                  <span className="ref-card__desc">{item.description}</span>
                </Link>
              ))}
            </div>
          </section>
        ))}
      </div>
    </section>
  )
}
