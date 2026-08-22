import { Link } from 'react-router-dom'
import type { ReactNode } from 'react'

export type HubItem = {
  to: string
  label: string
  description?: string
  icon?: string
  badge?: string | number
}

export type HubSection = {
  title: string
  icon?: string
  items: HubItem[]
}

type Breadcrumb = {
  label: string
  to?: string
}

type HubPageProps = {
  title: string
  subtitle?: string
  sections: HubSection[]
  breadcrumbs?: Breadcrumb[]
  actions?: ReactNode
}

export function HubPage({
  title,
  subtitle,
  sections,
  breadcrumbs,
  actions,
}: HubPageProps) {
  return (
    <section className="app-card app-card--wide">
      {breadcrumbs && breadcrumbs.length > 0 ? (
        <nav className="breadcrumbs" aria-label="Хлебные крошки" style={{ marginBottom: 12 }}>
          {breadcrumbs.map((crumb, index) => (
            <span key={index} className="breadcrumbs__item">
              {crumb.to ? (
                <Link to={crumb.to} className="breadcrumbs__link">
                  {crumb.label}
                </Link>
              ) : (
                <span className="breadcrumbs__current">{crumb.label}</span>
              )}
              {index < breadcrumbs.length - 1 ? (
                <span className="breadcrumbs__sep">/</span>
              ) : null}
            </span>
          ))}
        </nav>
      ) : null}

      <div className="hub-header">
        <div>
          <h1 className="page-title">{title}</h1>
          {subtitle ? <p className="hub-subtitle">{subtitle}</p> : null}
        </div>
        {actions ? <div className="hub-actions">{actions}</div> : null}
      </div>

      <div className="hub-sections">
        {sections.map((section) => (
          <section key={section.title} className="hub-section">
            <h2 className="hub-section__title">
              {section.icon ? (
                <span className="hub-section__icon" aria-hidden>
                  {section.icon}
                </span>
              ) : null}
              {section.title}
            </h2>
            <div className="hub-section__links">
              {section.items.map((item) => (
                <Link
                  key={item.to + item.label}
                  to={item.to}
                  className="hub-link"
                >
                  {item.icon ? (
                    <span className="hub-link__icon" aria-hidden>
                      {item.icon}
                    </span>
                  ) : null}
                  <span className="hub-link__content">
                    <span className="hub-link__label">{item.label}</span>
                    {item.description ? (
                      <span className="hub-link__desc">{item.description}</span>
                    ) : null}
                  </span>
                  {item.badge !== undefined ? (
                    <span className="hub-link__badge">{item.badge}</span>
                  ) : null}
                  <span className="hub-link__arrow" aria-hidden>
                    &rarr;
                  </span>
                </Link>
              ))}
            </div>
          </section>
        ))}
      </div>
    </section>
  )
}
