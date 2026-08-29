import { useEffect, useState } from 'react'
import { apiClient } from '../lib/apiClient'

type Order = { id: number; number: string; status: string }

export function PortalOrdersPage() {
  const [inbound, setInbound] = useState<Order[]>([])
  const [outbound, setOutbound] = useState<Order[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      apiClient.get<Order[]>('/api/v1/portal/orders/inbound'),
      apiClient.get<Order[]>('/api/v1/portal/orders/outbound'),
    ])
      .then(([a, b]) => {
        setInbound(a)
        setOutbound(b)
      })
      .catch((e) => setError(e instanceof Error ? e.message : 'Ошибка'))
  }, [])

  if (error) return <p className="app-card">{error}</p>

  return (
    <div className="app-card">
      <h1>Заказы</h1>
      <h2>Входящие</h2>
      <ul>
        {inbound.map((o) => (
          <li key={`in-${o.id}`}>
            {o.number} — {o.status}
          </li>
        ))}
      </ul>
      <h2>Исходящие</h2>
      <ul>
        {outbound.map((o) => (
          <li key={`out-${o.id}`}>
            {o.number} — {o.status}
          </li>
        ))}
      </ul>
    </div>
  )
}
