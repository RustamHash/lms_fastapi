import { useEffect, useState } from 'react'
import { apiClient } from '../lib/apiClient'

type StockRow = {
  product_id: number
  sku: string | null
  name: string | null
  location_id: number
  quantity: string
  reserved_quantity: string
}

export function PortalStockPage() {
  const [rows, setRows] = useState<StockRow[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    apiClient
      .get<StockRow[]>('/api/v1/portal/stock')
      .then(setRows)
      .catch((e) => setError(e instanceof Error ? e.message : 'Ошибка'))
  }, [])

  if (error) return <p className="app-card">{error}</p>

  return (
    <div className="app-card">
      <h1>Остатки</h1>
      <table>
        <thead>
          <tr>
            <th>SKU</th>
            <th>Название</th>
            <th>Ячейка</th>
            <th>Кол-во</th>
            <th>Резерв</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={`${r.product_id}-${r.location_id}-${i}`}>
              <td>{r.sku}</td>
              <td>{r.name}</td>
              <td>{r.location_id}</td>
              <td>{r.quantity}</td>
              <td>{r.reserved_quantity}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
