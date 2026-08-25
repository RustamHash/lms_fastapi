import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { DetailPageShell } from '../components/DetailPageShell'
import { PlanFactTabs, type PlanFact } from '../components/PlanFactTabs'
import { apiClient } from '../lib/apiClient'
import { formatDt } from '../lib/formatDt'
import { getDocumentStatusLabel, getDocumentTypeLabel } from '../lib/statusLabels'

type Document = {
  id: number
  document_number: string
  document_type: string
  status: string
  document_date: string | null
  warehouse_id: number
  is_delivery: boolean
  is_edo: boolean
}

export function DocumentDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [doc, setDoc] = useState<Document | null>(null)
  const [planFact, setPlanFact] = useState<PlanFact | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    ;(async () => {
      setLoading(true)
      setError(null)
      try {
        const [docData, snapshot] = await Promise.all([
          apiClient.get<Document>(`/api/v1/documents/${id}`),
          apiClient.get<PlanFact>(`/api/v1/documents/${id}/plan-fact`),
        ])
        setDoc(docData)
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
      title={`Документ${doc ? ` ${doc.document_number}` : ''}`}
      backHref="/documents"
      backLabel="← К документам"
      loading={loading}
      error={error}
    >
      {doc ? (
        <>
          <dl className="entity-dl">
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Номер</dt>
              <dd className="entity-dl__dd">{doc.document_number}</dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Тип</dt>
              <dd className="entity-dl__dd">{getDocumentTypeLabel(doc.document_type)}</dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Статус</dt>
              <dd className="entity-dl__dd">{getDocumentStatusLabel(doc.status)}</dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Дата</dt>
              <dd className="entity-dl__dd">
                {doc.document_date ? formatDt(doc.document_date) : '—'}
              </dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Склад ID</dt>
              <dd className="entity-dl__dd">{doc.warehouse_id}</dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">Доставка</dt>
              <dd className="entity-dl__dd">{doc.is_delivery ? 'Да' : 'Нет'}</dd>
            </div>
            <div className="entity-dl__row">
              <dt className="entity-dl__dt">ЭДО</dt>
              <dd className="entity-dl__dd">{doc.is_edo ? 'Да' : 'Нет'}</dd>
            </div>
          </dl>
          <PlanFactTabs data={planFact} />
        </>
      ) : null}
    </DetailPageShell>
  )
}
