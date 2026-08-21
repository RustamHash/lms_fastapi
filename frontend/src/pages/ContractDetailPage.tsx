import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { DetailPageShell } from '../components/DetailPageShell'
import { apiClient } from '../lib/apiClient'

type Contract = {
  id: number
  number: string
  customer_id: number
  executor_id: number
  contract_type: string
  start_date: string
  end_date: string | null
  status: string
  is_deleted: boolean
  is_active: boolean
}

export function ContractDetailPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const canEdit = user?.permissions?.all === true
  const { contractId } = useParams<{ contractId: string }>()
  const [contract, setContract] = useState<Contract | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!contractId) return
    ;(async () => {
      setLoading(true)
      try {
        const data = await apiClient.get<Contract>(`/api/v1/parties/contracts/${contractId}`)
        setContract(data)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Ошибка')
      } finally {
        setLoading(false)
      }
    })()
  }, [contractId])

  return (
    <DetailPageShell
      title={contract ? `Договор ${contract.number}` : 'Договор'}
      breadcrumbs={[
        { label: 'Справочники', to: '/references' },
        { label: 'Договоры', to: '/reference/contracts' },
        { label: contract ? contract.number : '' },
      ]}
      loading={loading}
      error={error}
      canEdit={canEdit}
      onEdit={() => navigate('edit')}
    >
      {contract ? (
        <dl className="entity-dl">
          <div className="entity-dl__row"><dt>ID</dt><dd>{contract.id}</dd></div>
          <div className="entity-dl__row"><dt>Номер</dt><dd>{contract.number}</dd></div>
          <div className="entity-dl__row"><dt>Тип</dt><dd>{contract.contract_type}</dd></div>
          <div className="entity-dl__row"><dt>Начало</dt><dd>{contract.start_date}</dd></div>
          <div className="entity-dl__row"><dt>Окончание</dt><dd>{contract.end_date || '—'}</dd></div>
          <div className="entity-dl__row"><dt>Статус</dt><dd>{contract.status}</dd></div>
        </dl>
      ) : null}
    </DetailPageShell>
  )
}
