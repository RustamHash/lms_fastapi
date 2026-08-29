import { useEffect, useState } from 'react'
import { apiClient } from '../lib/apiClient'

type Product = { id: number; sku: string; name: string }

export function PortalProductsPage() {
  const [rows, setRows] = useState<Product[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    apiClient
      .get<Product[]>('/api/v1/portal/products')
      .then(setRows)
      .catch((e) => setError(e instanceof Error ? e.message : 'Ошибка'))
  }, [])

  if (error) return <p className="app-card">{error}</p>

  return (
    <div className="app-card">
      <h1>Товары</h1>
      <table>
        <thead>
          <tr>
            <th>SKU</th>
            <th>Название</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td>{r.sku}</td>
              <td>{r.name}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
