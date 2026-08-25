import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth, hasPermission } from '../auth/AuthContext'
import { DetailPageShell } from '../components/DetailPageShell'
import { apiClient } from '../lib/apiClient'

type RoleBrief = { id: number; code: string; name: string }

type UserDetail = {
  id: number
  username: string
  phone: string
  email: string | null
  is_superuser: boolean
  is_active: boolean
  roles: RoleBrief[]
  depositor_ids: number[]
  client_ids: number[]
}

type DepositorOption = {
  id: number
  code: string
  legal_entity: { id: number; name: string } | null
}

type ClientOption = {
  id: number
  code: string
  name: string
  depositor_id: number
}

function toggleId(list: number[], id: number): number[] {
  return list.includes(id) ? list.filter((item) => item !== id) : [...list, id]
}

export function UserDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { user: currentUser } = useAuth()
  const canEdit = hasPermission(currentUser, 'users', 'update')
  const [user, setUser] = useState<UserDetail | null>(null)
  const [roles, setRoles] = useState<RoleBrief[]>([])
  const [depositors, setDepositors] = useState<DepositorOption[]>([])
  const [clients, setClients] = useState<ClientOption[]>([])
  const [phone, setPhone] = useState('')
  const [email, setEmail] = useState('')
  const [isActive, setIsActive] = useState(true)
  const [roleIds, setRoleIds] = useState<number[]>([])
  const [depositorIds, setDepositorIds] = useState<number[]>([])
  const [clientIds, setClientIds] = useState<number[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    let cancelled = false
    ;(async () => {
      setLoading(true)
      setError(null)
      try {
        const [userData, roleData, depositorData, clientData] = await Promise.all([
          apiClient.get<UserDetail>(`/api/v1/users/${id}`),
          apiClient.get<RoleBrief[]>('/api/v1/roles').catch(() => [] as RoleBrief[]),
          apiClient.get<DepositorOption[]>('/api/v1/depositors').catch(() => [] as DepositorOption[]),
          apiClient.get<ClientOption[]>('/api/v1/clients').catch(() => [] as ClientOption[]),
        ])
        if (cancelled) return
        setUser(userData)
        setPhone(userData.phone ?? '')
        setEmail(userData.email ?? '')
        setIsActive(userData.is_active)
        setRoleIds(userData.roles.map((role) => role.id))
        setDepositorIds(userData.depositor_ids)
        setClientIds(userData.client_ids ?? [])
        setRoles(roleData)
        setDepositors(depositorData)
        setClients(clientData)
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Ошибка загрузки')
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [id])

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!id || !canEdit) return
    setSaving(true)
    setError(null)
    try {
      const patched = await apiClient.patch<UserDetail>(`/api/v1/users/${id}`, {
        phone,
        email: email.trim() || null,
        is_active: isActive,
      })
      const withRoles = await apiClient.put<UserDetail>(`/api/v1/users/${id}/roles`, {
        role_ids: roleIds,
      })
      const withDepositors = await apiClient.put<UserDetail>(`/api/v1/users/${id}/depositors`, {
        depositor_ids: depositorIds,
      })
      const saved = await apiClient.put<UserDetail>(`/api/v1/users/${id}/clients`, {
        client_ids: clientIds.filter((clientId) => {
          const client = clients.find((row) => row.id === clientId)
          return client ? depositorIds.includes(client.depositor_id) : false
        }),
      })
      const next = { ...patched, ...withRoles, ...withDepositors, ...saved }
      setUser(next)
      setRoleIds(next.roles.map((role) => role.id))
      setDepositorIds(next.depositor_ids)
      setClientIds(next.client_ids ?? [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка сохранения')
    } finally {
      setSaving(false)
    }
  }

  return (
    <DetailPageShell
      title={user ? `Пользователь #${user.id}` : 'Пользователь'}
      backHref="/users"
      backLabel="← К пользователям"
      loading={loading}
      error={loading ? null : error && !user ? error : null}
    >
      {user ? (
        <form onSubmit={onSubmit} className="wh-form wh-form--wide">
          <label>
            ID
            <input value={user.id} disabled />
          </label>
          <label>
            Имя
            <input value={user.username} disabled />
          </label>
          <label>
            Телефон
            <input value={phone} onChange={(e) => setPhone(e.target.value)} disabled={!canEdit} />
          </label>
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={!canEdit}
            />
          </label>
          <p className="wh-form__hint">
            Суперпользователь: {user.is_superuser ? 'да' : 'нет'}
          </p>
          <label className="wh-form__check">
            <input
              type="checkbox"
              checked={isActive}
              onChange={(e) => setIsActive(e.target.checked)}
              disabled={!canEdit}
            />
            Активен
          </label>

          <fieldset className="wh-form__fieldset" disabled={!canEdit}>
            <legend>Роли</legend>
            {roles.length === 0 ? (
              <p className="wh-form__hint">Нет доступных ролей</p>
            ) : (
              roles.map((role) => (
                <label key={role.id} className="wh-form__check">
                  <input
                    type="checkbox"
                    checked={roleIds.includes(role.id)}
                    onChange={() => setRoleIds((prev) => toggleId(prev, role.id))}
                  />
                  {role.name} ({role.code})
                </label>
              ))
            )}
          </fieldset>

          <fieldset className="wh-form__fieldset" disabled={!canEdit}>
            <legend>Поклажедатели</legend>
            <p className="wh-form__hint">
              Пустой список — видит всех поклажедателей (сотрудник склада). Отмеченные —
              только свои (менеджер или агент поклажедателя).
            </p>
            {depositors.length === 0 ? (
              <p className="wh-form__hint">Нет доступных поклажедателей</p>
            ) : (
              depositors.map((depositor) => (
                <label key={depositor.id} className="wh-form__check">
                  <input
                    type="checkbox"
                    checked={depositorIds.includes(depositor.id)}
                    onChange={() => setDepositorIds((prev) => toggleId(prev, depositor.id))}
                  />
                  {depositor.legal_entity?.name || depositor.code || `#${depositor.id}`}
                </label>
              ))
            )}
          </fieldset>

          {depositorIds.length > 0 ? (
            <fieldset className="wh-form__fieldset" disabled={!canEdit}>
              <legend>Клиенты</legend>
              <p className="wh-form__hint">
                Пустой список — менеджер, видит всех клиентов выбранных поклажедателей.
                Отмеченные — торговый агент, только эти клиенты.
              </p>
              {clients.filter((client) => depositorIds.includes(client.depositor_id)).length === 0 ? (
                <p className="wh-form__hint">Нет клиентов у выбранных поклажедателей</p>
              ) : (
                clients
                  .filter((client) => depositorIds.includes(client.depositor_id))
                  .map((client) => (
                    <label key={client.id} className="wh-form__check">
                      <input
                        type="checkbox"
                        checked={clientIds.includes(client.id)}
                        onChange={() => setClientIds((prev) => toggleId(prev, client.id))}
                      />
                      {client.name} ({client.code})
                    </label>
                  ))
              )}
            </fieldset>
          ) : null}

          {error && user ? <p className="wh-form__err">{error}</p> : null}
          {canEdit ? (
            <div className="wh-form__actions">
              <button type="submit" disabled={saving}>
                {saving ? 'Сохранение...' : 'Сохранить'}
              </button>
            </div>
          ) : null}
        </form>
      ) : null}
    </DetailPageShell>
  )
}
