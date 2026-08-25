import { Link, useLocation } from 'react-router-dom'

type Props = {
  /** Страницы под `/reference/topology/*` — показывать ссылку всегда */
  always?: boolean
}

export function TopologyBackBar({ always = false }: Props) {
  const { state } = useLocation() as { state?: { fromTopology?: boolean } }
  const show = always || Boolean(state?.fromTopology)
  if (!show) return null
  return (
    <div className="topology-back-bar" role="navigation" aria-label="Назад к разделу «Топология»">
      <Link to="/topology" className="topology-back-bar__link">
        ← Топология
      </Link>
    </div>
  )
}
