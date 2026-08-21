import { memo, type ReactNode } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { TopologyBackBar } from './TopologyBackBar'

type Breadcrumb = {
  label: string
  to?: string
}

type DetailPageShellProps = {
  title: string
  backHref?: string
  backLabel?: string
  backState?: unknown
  backContent?: ReactNode
  subtitle?: ReactNode
  breadcrumbs?: Breadcrumb[]
  canEdit?: boolean
  onEdit?: () => void | Promise<void>
  editPath?: string
  loading?: boolean
  error?: string | null
  children?: ReactNode
}

function DetailPageShellInner({
  title,
  backHref,
  backLabel,
  backState,
  backContent,
  subtitle,
  breadcrumbs,
  canEdit = false,
  onEdit,
  editPath,
  loading = false,
  error = null,
  children,
}: DetailPageShellProps) {
  const navigate = useNavigate()

  function handleBack() {
    if (window.history.length > 1) {
      navigate(-1)
    } else if (backHref) {
      navigate(backHref)
    }
  }

  return (
    <section className="app-card app-card--wide">
      <TopologyBackBar />

      {/* Кнопка назад */}
      <div className="detail-nav">
        <button type="button" className="detail-nav__back" onClick={handleBack}>
          ← Назад
        </button>

        {/* Хлебные крошки */}
        {breadcrumbs && breadcrumbs.length > 0 ? (
          <nav className="breadcrumbs" aria-label="Хлебные крошки">
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
      </div>

      {backContent ? <p className="entity-detail__back">{backContent}</p> : null}
      {!backContent && backHref && backLabel ? (
        <p className="entity-detail__back">
          <Link to={backHref} state={backState}>
            {backLabel}
          </Link>
        </p>
      ) : null}

      <div className="detail-header">
        <h1 className="page-title">{title}</h1>
        {canEdit && (onEdit || editPath) ? (
          onEdit ? (
            <button type="button" className="tb tb--view" onClick={() => void onEdit()}>
              Редактировать
            </button>
          ) : editPath ? (
            <Link to={editPath} className="tb tb--view">
              Редактировать
            </Link>
          ) : null
        ) : null}
      </div>
      {subtitle ? <p className="entity-detail__subtitle">{subtitle}</p> : null}
      {loading ? <p>Загрузка…</p> : null}
      {!loading && error ? (
        <p className="list-msg list-msg--err" role="alert">
          {error}
        </p>
      ) : null}
      {!loading && !error ? children : null}
    </section>
  )
}


export const DetailPageShell = memo(DetailPageShellInner)
