import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { DetailPageShell } from '../components/DetailPageShell'
import { PlanFactTabs, type PlanFact } from '../components/PlanFactTabs'
import { apiClient } from '../lib/apiClient'
import { formatDt } from '../lib/formatDt'
import { getStatusLabel } from '../lib/statusLabels'

type OutboundOrder = {
  id: number
  number: string
  customer_code: string
  customer_name: string
  delivery_address_name: string
  order_date: string
  shipping_date: string | null
  status: string
  needs_delivery: boolean
  notes: string
  declared_weight: string | null
}

export function OutboundOrderDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [order, setOrder] = useState<OutboundOrder | null>(null)
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
          apiClient.get<OutboundOrder>(`/api/v1/outbound-orders/${id}`),
          apiClient.get<PlanFact>(`/api/v1/warehouse/picking/outbound/${id}`),
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
      title={`Исходящий заказ${order ? ` ${order.number}` : ''}`}
      backHref="/orders/outbound"
      backLabel="← К исходящим заказам"
      loading={loading}
      error={error}
    >
      {order ? (
        <>
          <dl className="entity-dl">
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Номер</dt>
              <dd className="entity-dl__dd">{order.number}</dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Клиент</dt>
              <dd className="entity-dl__dd">
                {order.customer_name || order.customer_code || '—'}
              </dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Адрес доставки</dt>
              <dd className="entity-dl__dd">{order.delivery_address_name || '—'}</dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Дата заявки</dt>
              <dd className="entity-dl__dd">{formatDt(order.order_date)}</dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Дата отгрузки</dt>
              <dd className="entity-dl__dd">
                {order.shipping_date ? formatDt(order.shipping_date) : '—'}
              </dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Статус</dt>
              <dd className="entity-dl__dd">{getStatusLabel(order.status)}</dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Доставка</dt>
              <dd className="entity-dl__dd">{order.needs_delivery ? 'Да' : 'Нет'}</dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Вес</dt>
              <dd className="entity-dl__dd">{order.declared_weight ?? '—'}</dd>
            </div>
          </dl>
          <PlanFactTabs data={planFact} />
        </>
      ) : null}
    </DetailPageShell>
  )
}
