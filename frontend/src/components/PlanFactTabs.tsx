import { useState } from 'react'
import { formatDate, formatDt } from '../lib/formatDt'
import { DetailDataTable } from './DetailDataTable'

export type PlanLine = {
  id: number
  product_id: number | null
  product_sku: string
  product_name: string
  quantity: string
  batch_number: string
  manufacture_date: string | null
}

export type FactMovement = {
  id: number
  moved_at: string
  direction: string
  quantity: string
  product_id: number
  product_sku: string
  product_name: string
  batch_number: string
  lpn_number: string
  location_id: number
  production_date: string | null
  expiration_date: string | null
  remaining_days: number | null
  remaining_percent: string | null
}

export type Discrepancy = {
  inbound_order_line_id?: number | null
  product_id: number | null
  product_sku: string
  product_name: string
  qty_planned: string
  qty_fact: string
  qty_diff: string
  kind: 'match' | 'shortage' | 'surplus' | string
}

export type PlanFact = {
  plan: PlanLine[]
  fact: FactMovement[]
  discrepancies: Discrepancy[]
}

type Tab = 'plan' | 'fact' | 'discrepancies'

const KIND_LABEL: Record<string, string> = {
  match: 'Сошлось',
  shortage: 'Недогруз',
  surplus: 'Излишек',
}

const DIR_LABEL: Record<string, string> = {
  in: 'Приход',
  out: 'Списание',
}

type Props = {
  data: PlanFact | null
}

export function PlanFactTabs({ data }: Props) {
  const [tab, setTab] = useState<Tab>('plan')
  const plan = data?.plan ?? []
  const fact = data?.fact ?? []
  const discrepancies = data?.discrepancies ?? []
  const mismatchCount = discrepancies.filter((d) => d.kind !== 'match').length

  return (
    <>
      <div className="entity-tabs">
        <button
          type="button"
          className={`entity-tabs__btn${tab === 'plan' ? ' entity-tabs__btn--active' : ''}`}
          onClick={() => setTab('plan')}
        >
          План ({plan.length})
        </button>
        <button
          type="button"
          className={`entity-tabs__btn${tab === 'fact' ? ' entity-tabs__btn--active' : ''}`}
          onClick={() => setTab('fact')}
        >
          Факт ({fact.length})
        </button>
        <button
          type="button"
          className={`entity-tabs__btn${tab === 'discrepancies' ? ' entity-tabs__btn--active' : ''}`}
          onClick={() => setTab('discrepancies')}
        >
          Расхождения ({mismatchCount})
        </button>
      </div>

      {tab === 'plan' ? (
        <div className="entity-tab-panel">
          <DetailDataTable
            columns={[
              { id: 'id', label: 'ID', render: (row) => row.id },
              { id: 'product_name', label: 'Товар', render: (row) => row.product_name || '—' },
              { id: 'product_sku', label: 'Артикул', render: (row) => row.product_sku || '—' },
              { id: 'quantity', label: 'План', render: (row) => row.quantity },
              { id: 'batch_number', label: 'Партия', render: (row) => row.batch_number || '—' },
              {
                id: 'manufacture_date',
                label: 'Дата изготовления',
                render: (row) => formatDate(row.manufacture_date),
              },
            ]}
            rows={plan}
            empty="Нет строк"
            rowKey={(row) => row.id}
          />
        </div>
      ) : null}

      {tab === 'fact' ? (
        <div className="entity-tab-panel">
          <DetailDataTable
            columns={[
              { id: 'moved_at', label: 'Когда', render: (row) => formatDt(row.moved_at) },
              {
                id: 'direction',
                label: 'Направление',
                render: (row) => DIR_LABEL[row.direction] ?? row.direction,
              },
              { id: 'product_name', label: 'Товар', render: (row) => row.product_name || '—' },
              { id: 'product_sku', label: 'Артикул', render: (row) => row.product_sku || '—' },
              { id: 'quantity', label: 'Кол-во', render: (row) => row.quantity },
              { id: 'batch_number', label: 'Партия', render: (row) => row.batch_number || '—' },
              {
                id: 'production_date',
                label: 'Дата изготовления',
                render: (row) => formatDate(row.production_date),
              },
              {
                id: 'expiration_date',
                label: 'Срок годности',
                render: (row) => formatDate(row.expiration_date),
              },
              {
                id: 'remaining_days',
                label: 'Ост. срок, дн.',
                render: (row) => (row.remaining_days == null ? '—' : row.remaining_days),
              },
              {
                id: 'remaining_percent',
                label: 'Ост. срок, %',
                render: (row) =>
                  row.remaining_percent == null || row.remaining_percent === ''
                    ? '—'
                    : `${row.remaining_percent}%`,
              },
              { id: 'lpn_number', label: 'LPN', render: (row) => row.lpn_number || '—' },
              { id: 'location_id', label: 'Ячейка', render: (row) => row.location_id },
            ]}
            rows={fact}
            empty="Движений нет"
            rowKey={(row) => row.id}
          />
        </div>
      ) : null}

      {tab === 'discrepancies' ? (
        <div className="entity-tab-panel">
          <DetailDataTable
            columns={[
              { id: 'product_name', label: 'Товар', render: (row) => row.product_name || '—' },
              { id: 'product_sku', label: 'Артикул', render: (row) => row.product_sku || '—' },
              { id: 'qty_planned', label: 'План', render: (row) => row.qty_planned },
              { id: 'qty_fact', label: 'Факт', render: (row) => row.qty_fact },
              { id: 'qty_diff', label: 'Разница', render: (row) => row.qty_diff },
              { id: 'kind', label: 'Сверка', render: (row) => KIND_LABEL[row.kind] ?? row.kind },
            ]}
            rows={discrepancies}
            empty="Нечего сверять — нет строк"
            rowKey={(row, index) => `${row.product_id ?? 'x'}-${index}`}
            rowClassName={(row) =>
              row.kind === 'match' ? undefined : `detail-data-table__row--${row.kind}`
            }
          />
        </div>
      ) : null}
    </>
  )
}
