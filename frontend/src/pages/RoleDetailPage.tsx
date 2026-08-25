import { useEffect, useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth, hasPermission } from '../auth/AuthContext'
import { DetailPageShell } from '../components/DetailPageShell'
import { apiClient } from '../lib/apiClient'

type RoleDetail = {
  id: number
  name: string
  code: string
  permissions: Record<string, string[]>
}

type AvailablePermissions = {
  modules: string[]
  actions: string[]
  module_labels: Record<string, string>
  action_labels: Record<string, string>
}

export function RoleDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const canEdit = hasPermission(user, 'roles', 'update')
  const [role, setRole] = useState<RoleDetail | null>(null)
  const [available, setAvailable] = useState<AvailablePermissions | null>(null)
  const [name, setName] = useState('')
  const [code, setCode] = useState('')
  const [permissions, setPermissions] = useState<Record<string, string[]>>({})
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
        const [roleData, catalog] = await Promise.all([
          apiClient.get<RoleDetail>(`/api/v1/roles/${id}`),
          apiClient.get<AvailablePermissions>('/api/v1/permissions/available'),
        ])
        if (cancelled) return
        setRole(roleData)
        setName(roleData.name)
        setCode(roleData.code)
        setPermissions(roleData.permissions ?? {})
        setAvailable(catalog)
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

  const modules = available?.modules ?? []
  const actions = available?.actions ?? []

  const matrix = useMemo(() => {
    const set = new Set<string>()
    for (const [module, moduleActions] of Object.entries(permissions)) {
      for (const action of moduleActions) set.add(`${module}:${action}`)
    }
    return set
  }, [permissions])

  function toggle(module: string, action: string) {
    setPermissions((prev) => {
      const current = new Set(prev[module] ?? [])
      if (current.has(action)) current.delete(action)
      else current.add(action)
      const next = { ...prev }
      if (current.size === 0) delete next[module]
      else next[module] = actions.filter((item) => current.has(item))
      return next
    })
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!id || !canEdit) return
    setSaving(true)
    setError(null)
    try {
      const saved = await apiClient.patch<RoleDetail>(`/api/v1/roles/${id}`, {
        name,
        code,
        permissions,
      })
      setRole(saved)
      setName(saved.name)
      setCode(saved.code)
      setPermissions(saved.permissions ?? {})
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка сохранения')
    } finally {
      setSaving(false)
    }
  }

  return (
    <DetailPageShell
      title={role ? `Роль #${role.id}` : 'Роль'}
      backHref="/roles"
      backLabel="← К ролям"
      loading={loading}
      error={loading ? null : error && !role ? error : null}
    >
      {role ? (
        <form onSubmit={onSubmit} className="wh-form wh-form--wide">
          <label>
            Название
            <input value={name} onChange={(e) => setName(e.target.value)} disabled={!canEdit} required />
          </label>
          <label>
            Код
            <input value={code} onChange={(e) => setCode(e.target.value)} disabled={!canEdit} required />
          </label>

          <div className="perm-matrix-wrap">
            <p className="wh-form__hint">Права: модуль × действие</p>
            <table className="perm-matrix">
              <thead>
                <tr>
                  <th>Модуль</th>
                  {actions.map((action) => (
                    <th key={action}>{available?.action_labels[action] ?? action}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {modules.map((module) => (
                  <tr key={module}>
                    <td>{available?.module_labels[module] ?? module}</td>
                    {actions.map((action) => (
                      <td key={action}>
                        <input
                          type="checkbox"
                          checked={matrix.has(`${module}:${action}`)}
                          onChange={() => toggle(module, action)}
                          disabled={!canEdit}
                          aria-label={`${module} ${action}`}
                        />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {error && role ? <p className="wh-form__err">{error}</p> : null}
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
