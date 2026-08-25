import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { DetailPageShell } from '../components/DetailPageShell'
import { PlanFactTabs, type PlanFact } from '../components/PlanFactTabs'
import { apiClient } from '../lib/apiClient'
import { formatDate } from '../lib/formatDt'
import { getStatusLabel } from '../lib/statusLabels'

type InboundOrder = {
  id: number
  number: string
  order_number: string
  loc_code: string
  warehouse_id: number | null
  warehouse_name: string
  supplier_code: string
  order_date: string
  planned_date: string | null
  notes: string
  status: string
  has_shortage: boolean
}

export function InboundOrderDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [order, setOrder] = useState<InboundOrder | null>(null)
  const [planFact, setPlanFact] = useState<PlanFact | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    ;(async () => {
      setLoading(true)
      setError(null)
      try {
        const [orderData, snapshot] = await Promise.all([
          apiClient.get<InboundOrder>(`/api/v1/inbound-orders/${id}`),
          apiClient.get<PlanFact>(`/api/v1/warehouse/receiving/inbound/${id}`),
        ])
        setOrder(orderData)
        setPlanFact(snapshot)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Ошибка загрузки')
      } finally {
        setLoading(false)
      }
    })()
  }, [id])

  return (
    <DetailPageShell
      title={`Входящий заказ${order ? ` ${order.number}` : ''}`}
      backHref="/orders/inbound"
      backLabel="← К входящим заказам"
      loading={loading}
      error={error}
    >
      {order ? (
        <>
          <dl className="entity-dl">
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Номер заявки</dt>
              <dd className="entity-dl__dd">{order.number}</dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Номер заказа</dt>
              <dd className="entity-dl__dd">{order.order_number || '—'}</dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Склад (LOC)</dt>
              <dd className="entity-dl__dd">{order.loc_code || '—'}</dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Склад</dt>
              <dd className="entity-dl__dd">
                {order.warehouse_name
                  || (order.warehouse_id != null ? `#${order.warehouse_id}` : '—')}
              </dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Поставщик</dt>
              <dd className="entity-dl__dd">{order.supplier_code || '—'}</dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Дата заявки</dt>
              <dd className="entity-dl__dd">{formatDate(order.order_date)}</dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Плановая дата</dt>
              <dd className="entity-dl__dd">{formatDate(order.planned_date)}</dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Статус</dt>
              <dd className="entity-dl__dd">{getStatusLabel(order.status)}</dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Недогруз</dt>
              <dd className="entity-dl__dd">{order.has_shortage ? 'Да' : 'Нет'}</dd>
            </div>
          </dl>
          <PlanFactTabs data={planFact} />
        </>
      ) : null}
    </DetailPageShell>
  )
}
