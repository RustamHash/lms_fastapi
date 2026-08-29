import { useEffect, useState } from 'react'
import { apiClient } from '../lib/apiClient'

type Dashboard = {
  depositor_id: number
  inbound_orders: number
  outbound_orders: number
  products: number
}

export function PortalHomePage() {
  const [data, setData] = useState<Dashboard | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    apiClient
      .get<Dashboard>('/api/v1/portal/dashboard')
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : 'Ошибка'))
  }, [])

  if (error) return <p className="app-card">{error}</p>
  if (!data) return <p className="app-card">Загрузка...</p>

  return (
    <div className="app-card">
      <h1>Сводка</h1>
      <p>Поклажедатель ID: {data.depositor_id}</p>
      <ul>
        <li>Входящие заказы: {data.inbound_orders}</li>
        <li>Исходящие заказы: {data.outbound_orders}</li>
        <li>Товары: {data.products}</li>
      </ul>
    </div>
  )
}
