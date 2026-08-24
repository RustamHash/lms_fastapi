import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { DetailPageShell } from '../components/DetailPageShell'
import { apiClient } from '../lib/apiClient'

type TariffDocument = {
  id: number
  contract_id: number
  document_type: string
  number: string
  date: string
  valid_from: string
  valid_until: string | null
  currency: string
  vat_rate: string
  created_at: string
  updated_at: string
}

export function TariffDocumentDetailPage() {
  const { docId } = useParams<{ docId: string }>()
  const [doc, setDoc] = useState<TariffDocument | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!docId) return
    ;(async () => {
      setLoading(true)
      try {
        const data = await apiClient.get<TariffDocument>(`/api/v1/tariff-documents/${docId}`)
        setDoc(data)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Ошибка')
      } finally {
        setLoading(false)
      }
    })()
  }, [docId])

  return (
    <DetailPageShell
      title={doc ? `Документ ${doc.number}` : 'Документ тарифа'}
      backHref="/reference/tariff-documents"
      backLabel="← К документам тарифов"
      loading={loading}
      error={error}
    >
      {doc ? (
        <dl className="entity-dl">
          <div className="entity-dl__row"><dt>ID</dt><dd>{doc.id}</dd></div>
          <div className="entity-dl__row"><dt>Номер</dt><dd>{doc.number}</dd></div>
          <div className="entity-dl__row"><dt>Тип документа</dt><dd>{doc.document_type}</dd></div>
          <div className="entity-dl__row"><dt>Договор ID</dt><dd>{doc.contract_id}</dd></div>
          <div className="entity-dl__row"><dt>Дата</dt><dd>{doc.date}</dd></div>
          <div className="entity-dl__row"><dt>Действует с</dt><dd>{doc.valid_from}</dd></div>
          <div className="entity-dl__row"><dt>Действует до</dt><dd>{doc.valid_until ?? '—'}</dd></div>
          <div className="entity-dl__row"><dt>Валюта</dt><dd>{doc.currency}</dd></div>
          <div className="entity-dl__row"><dt>НДС</dt><dd>{doc.vat_rate}%</dd></div>
        </dl>
      ) : null}
    </DetailPageShell>
  )
}
