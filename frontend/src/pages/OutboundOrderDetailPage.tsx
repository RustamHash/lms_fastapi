import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { DetailPageShell } from '../components/DetailPageShell'
import { apiClient } from '../lib/apiClient'
import { formatDt } from '../lib/formatDt'
import { getStatusLabel, getDocumentTypeLabel, getDocumentStatusLabel, getTaskTypeLabel } from '../lib/statusLabels'

type DeliveryAddress = {
  id: number
  full_address: string
  delivery_zone: { id: number; name: string } | null
}

type OutboundOrderDetail = {
  id: number
  number: string
  customer_code: string
  customer_name: string
  status: string
  status_label?: string
  is_edo: boolean
  warehouse_id: number
  declared_weight: string | null
  needs_delivery: boolean
  notes: string
  depositor: { id: number; code: string; legal_entity_name: string } | null
  client: { id: number; code: string; name: string; delivery_address_id: number } | null
  warehouse: { id: number; name: string } | null
  delivery_address: DeliveryAddress | null
  zone: { id: number; name: string } | null
  delivery_order: Record<string, unknown> | null
  route: { id: number; number: string } | null
  driver: { id: number; name: string; phone: string } | null
  documents: Array<{ id: number; document_number: string; document_type: string; status: string }>
  tasks: Array<{ id: number; task_type: string; status: string }>
  returns: Array<{ id: number; return_date: string; status: string; return_type: string }>
}

type OrderLine = {
  id: number
  order_id: number
  product_id: number | null
  quantity: string
  location_id: number | null
  batch_number: string
  manufacture_date: string | null
  product_name: string
  product_sku: string
  location_name: string | null
}

export function OutboundOrderDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [order, setOrder] = useState<OutboundOrderDetail | null>(null)
  const [lines, setLines] = useState<OrderLine[]>([])
  const [activeTab, setActiveTab] = useState<'main' | 'lines' | 'delivery' | 'documents' | 'tasks'>('main')
  const [loading, setLoading] = useState(true)
  const [linesLoading, setLinesLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    ;(async () => {
      setLoading(true)
      try {
        const data = await apiClient.get<OutboundOrderDetail>(`/api/v1/outbound-orders/${id}/detail`)
        setOrder(data)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Ошибка')
      } finally {
        setLoading(false)
      }
    })()
  }, [id])

  useEffect(() => {
    if (activeTab !== 'lines' || !id) return
    ;(async () => {
      setLinesLoading(true)
      try {
        const data = await apiClient.get<OrderLine[]>(`/api/v1/outbound-orders/${id}/lines/enriched`)
        setLines(data)
      } catch (e) {
        console.error('Ошибка загрузки строк:', e)
      } finally {
        setLinesLoading(false)
      }
    })()
  }, [activeTab, id])

  return (
    <DetailPageShell
      title={`Исходящий заказ${order ? ` ${order.number}` : ''}`}
      backHref="/orders/outbound"
      backLabel="← К исходящим заказам"
      loading={loading}
      error={error}
    >
      {!loading && !error && order ? (
        <>
          <div className="entity-tabs">
            <button
              type="button"
              className={`entity-tabs__btn${activeTab === 'main' ? ' entity-tabs__btn--active' : ''}`}
              onClick={() => setActiveTab('main')}
            >
              Основное
            </button>
            <button
              type="button"
              className={`entity-tabs__btn${activeTab === 'lines' ? ' entity-tabs__btn--active' : ''}`}
              onClick={() => setActiveTab('lines')}
            >
              Строки ({lines.length || '...'})
            </button>
            <button
              type="button"
              className={`entity-tabs__btn${activeTab === 'delivery' ? ' entity-tabs__btn--active' : ''}`}
              onClick={() => setActiveTab('delivery')}
            >
              Доставка
            </button>
            <button
              type="button"
              className={`entity-tabs__btn${activeTab === 'documents' ? ' entity-tabs__btn--active' : ''}`}
              onClick={() => setActiveTab('documents')}
            >
              Документы ({(order.documents ?? []).length})
            </button>
            <button
              type="button"
              className={`entity-tabs__btn${activeTab === 'tasks' ? ' entity-tabs__btn--active' : ''}`}
              onClick={() => setActiveTab('tasks')}
            >
              Задания ({(order.tasks ?? []).length})
            </button>
          </div>

          {activeTab === 'main' ? (
            <div className="entity-grid">
              {/* Заказ */}
              <section className="entity-block">
                <h3 className="entity-block__title">Заказ</h3>
                <dl className="entity-dl">
                  <div className="entity-dl__row"><dt>ID</dt><dd>{order.id}</dd></div>
                  <div className="entity-dl__row"><dt>Номер</dt><dd>{order.number}</dd></div>
                  <div className="entity-dl__row"><dt>Статус</dt><dd>{order.status_label ?? getStatusLabel(order.status)}</dd></div>
                  <div className="entity-dl__row"><dt>ЭДО</dt><dd>{order.is_edo ? 'Да' : 'Нет'}</dd></div>
                  <div className="entity-dl__row"><dt>Вес</dt><dd>{order.declared_weight ?? '—'}</dd></div>
                  <div className="entity-dl__row"><dt>Доставка</dt><dd>{order.needs_delivery ? 'Да' : 'Нет'}</dd></div>
                </dl>
              </section>

              {/* Клиент */}
              {order.client ? (
                <section className="entity-block">
                  <h3 className="entity-block__title">Клиент</h3>
                  <dl className="entity-dl">
                    <div className="entity-dl__row"><dt>Название</dt><dd>{order.client.name}</dd></div>
                    <div className="entity-dl__row"><dt>Код</dt><dd>{order.client.code}</dd></div>
                  </dl>
                </section>
              ) : null}

              {/* Поклажедатель */}
              {order.depositor ? (
                <section className="entity-block">
                  <h3 className="entity-block__title">Поклажедатель</h3>
                  <dl className="entity-dl">
                    <div className="entity-dl__row"><dt>Код</dt><dd>{order.depositor.code}</dd></div>
                    <div className="entity-dl__row"><dt>Название</dt><dd>{order.depositor.legal_entity_name || '—'}</dd></div>
                  </dl>
                </section>
              ) : null}

              {/* Склад */}
              {order.warehouse ? (
                <section className="entity-block">
                  <h3 className="entity-block__title">Склад</h3>
                  <dl className="entity-dl">
                    <div className="entity-dl__row"><dt>Название</dt><dd>{order.warehouse.name}</dd></div>
                  </dl>
                </section>
              ) : null}

              {/* Адрес доставки */}
              {order.delivery_address ? (
                <section className="entity-block">
                  <h3 className="entity-block__title">Адрес доставки</h3>
                  <dl className="entity-dl">
                    <div className="entity-dl__row"><dt>Адрес</dt><dd>{order.delivery_address.full_address}</dd></div>
                    {order.delivery_address.delivery_zone ? (
                      <div className="entity-dl__row"><dt>Зона</dt><dd>{order.delivery_address.delivery_zone.name}</dd></div>
                    ) : null}
                  </dl>
                </section>
              ) : null}

              {/* Зона */}
              {order.zone ? (
                <section className="entity-block">
                  <h3 className="entity-block__title">Зона доставки</h3>
                  <dl className="entity-dl">
                    <div className="entity-dl__row"><dt>Название</dt><dd>{order.zone.name}</dd></div>
                  </dl>
                </section>
              ) : null}
            </div>
          ) : null}

          {activeTab === 'lines' ? (
            <div className="entity-tab-panel">
              {linesLoading ? (
                <p>Загрузка строк...</p>
              ) : lines.length === 0 ? (
                <p className="list-msg list-msg--warn">Нет строк</p>
              ) : (
                <table className="entity-related-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Товар</th>
                      <th>Артикул</th>
                      <th>Количество</th>
                      <th>Ячейка</th>
                      <th>Партия</th>
                      <th>Дата производства</th>
                    </tr>
                  </thead>
                  <tbody>
                    {lines.map((line) => (
                      <tr key={line.id}>
                        <td>{line.id}</td>
                        <td>{line.product_name || '—'}</td>
                        <td>{line.product_sku || '—'}</td>
                        <td>{line.quantity}</td>
                        <td>{line.location_name ?? (line.location_id ? String(line.location_id) : '—')}</td>
                        <td>{line.batch_number || '—'}</td>
                        <td>{line.manufacture_date ? formatDt(line.manufacture_date) : '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          ) : null}

          {activeTab === 'documents' ? (
            <div className="entity-tab-panel">
              {(order.documents ?? []).length === 0 ? (
                <p className="list-msg list-msg--warn">Нет документов</p>
              ) : (
                <table className="entity-related-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Номер</th>
                      <th>Тип</th>
                      <th>Статус</th>
                    </tr>
                  </thead>
                  <tbody>
                    {order.documents.map((doc) => (
                      <tr key={doc.id}>
                        <td>{doc.id}</td>
                        <td>{doc.document_number}</td>
                        <td>{getDocumentTypeLabel(doc.document_type)}</td>
                        <td>{getDocumentStatusLabel(doc.status)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          ) : null}

          {activeTab === 'tasks' ? (
            <div className="entity-tab-panel">
              {(order.tasks ?? []).length === 0 ? (
                <p className="list-msg list-msg--warn">Нет заданий</p>
              ) : (
                <table className="entity-related-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Тип</th>
                      <th>Статус</th>
                    </tr>
                  </thead>
                  <tbody>
                    {order.tasks.map((task) => (
                      <tr key={task.id}>
                        <td>{task.id}</td>
                        <td>{getTaskTypeLabel(task.task_type)}</td>
                        <td>{getStatusLabel(task.status)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          ) : null}

          {activeTab === 'delivery' ? (
            <div className="entity-tab-panel">
              <div className="entity-grid">
                {order.delivery_order ? (
                  <section className="entity-block">
                    <h3 className="entity-block__title">Заявка на доставку</h3>
                    <pre className="entity-json-view">{JSON.stringify(order.delivery_order, null, 2)}</pre>
                  </section>
                ) : (
                  <p className="list-msg list-msg--warn">Нет заявки на доставку</p>
                )}

                {order.route ? (
                  <section className="entity-block">
                    <h3 className="entity-block__title">Маршрут</h3>
                    <dl className="entity-dl">
                      <div className="entity-dl__row"><dt>Номер</dt><dd>{order.route.number}</dd></div>
                    </dl>
                  </section>
                ) : (
                  <p className="list-msg list-msg--warn">Маршрут не назначен</p>
                )}

                {order.driver ? (
                  <section className="entity-block">
                    <h3 className="entity-block__title">Водитель</h3>
                    <dl className="entity-dl">
                      <div className="entity-dl__row"><dt>ФИО</dt><dd>{order.driver.name}</dd></div>
                      <div className="entity-dl__row"><dt>Телефон</dt><dd>{order.driver.phone || '—'}</dd></div>
                    </dl>
                  </section>
                ) : (
                  <p className="list-msg list-msg--warn">Водитель не назначен</p>
                )}
              </div>
            </div>
          ) : null}
        </>
      ) : null}
    </DetailPageShell>
  )
}
