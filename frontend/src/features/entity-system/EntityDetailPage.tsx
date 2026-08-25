import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { DetailPageShell } from '../../components/DetailPageShell'
import { useAppNotice } from '../../notifications/AppNoticeContext'
import { useEntityDetail } from './hooks/useEntityDetail'
import type { EntityDetailConfig } from './types'

type Props<T extends { id: number }> = {
  config: EntityDetailConfig<T>
  id: number
}

export function EntityDetailPage<T extends { id: number }>({ config, id }: Props<T>) {
  const location = useLocation()
  const navigate = useNavigate()
  const { notify } = useAppNotice()
  const { data, loading, error, editing, deleting, setEditing, save, remove } =
    useEntityDetail<T>({ entityKey: config.entityKey, apiUrl: config.apiUrl, id })
  
  const [activeTab, setActiveTab] = useState<string>(
    config.tabs?.[0]?.id ?? 'main'
  )
  
  async function handleDelete() {
    if (!data) return
    if (!window.confirm('Удалить запись?')) return
    
    try {
      await remove()
      notify('Запись удалена', 'success')
      navigate(config.backUrl)
    } catch (e) {
      notify(e instanceof Error ? e.message : 'Ошибка удаления', 'error')
    }
  }
  
  const EditForm = config.editForm
  
  return (
    <DetailPageShell
      title={`${config.title}${data ? ` #${data.id}` : ''}`}
      backHref={config.backUrl}
      backLabel={config.backLabel ?? '← Назад'}
      backState={location.state}
      loading={loading}
      error={error}
    >
      {!loading && !error && data ? (
        <>
          {config.actions?.edit !== false || config.actions?.custom?.length ? (
            <div className="entity-inline-form">
              {config.actions?.edit !== false ? (
                <button
                  type="button"
                  className="tb tb--view"
                  onClick={() => setEditing(true)}
                >
                  Редактировать
                </button>
              ) : null}
              
              {config.actions?.delete !== false ? (
                <button
                  type="button"
                  className="tb tb--danger"
                  onClick={() => void handleDelete()}
                  disabled={deleting}
                >
                  {deleting ? 'Удаление…' : 'Удалить'}
                </button>
              ) : null}
              
              {config.actions?.custom?.map((action) => (
                <button
                  key={action.id}
                  type="button"
                  className="tb tb--view"
                  onClick={() => {
                    if (action.confirmMessage && !window.confirm(action.confirmMessage)) return
                    action.action(data, {
                      reload: () => void save({}),
                      notify,
                    })
                  }}
                  disabled={action.condition ? !action.condition(data) : false}
                >
                  {action.label}
                </button>
              ))}
            </div>
          ) : null}
          
          {config.tabs && config.tabs.length > 0 ? (
            <>
              <div className="entity-tabs" role="tablist">
                {config.tabs.map((tab) => (
                  <button
                    key={tab.id}
                    type="button"
                    role="tab"
                    aria-selected={activeTab === tab.id}
                    className={`entity-tabs__btn${activeTab === tab.id ? ' entity-tabs__btn--active' : ''}`}
                    onClick={() => setActiveTab(tab.id)}
                    disabled={tab.condition ? !tab.condition(data) : false}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
              
              {config.tabs.map((tab) => {
                if (activeTab !== tab.id) return null
                const TabComponent = tab.component
                return (
                  <div
                    key={tab.id}
                    role="tabpanel"
                    className="entity-tab-panel"
                  >
                    <TabComponent
                      entity={data}
                      onUpdate={async (patch) => { await save(patch) }}
                      reload={() => void save({})}
                      notify={notify}
                    />
                  </div>
                )
              })}
            </>
          ) : null}
          
          {config.sections && config.sections.length > 0 ? (
            <div className="entity-grid">
              {config.sections.map((section) => (
                <section key={section.id} className="entity-block">
                  <h3 className="entity-block__title">{section.title}</h3>
                  <dl className="entity-dl">
                    {section.fields.map((field) => {
                      const value = data[field.key]
                      const displayValue = field.format
                        ? field.format(value)
                        : value == null
                          ? '—'
                          : String(value)
                      
                      return (
                        <div key={String(field.key)} className="entity-dl__row">
                          <dt className="entity-dl__dt">{field.label}</dt>
                          <dd className="entity-dl__dd">
                            {field.type === 'link' && field.href ? (
                              <Link to={field.href(data)}>{displayValue}</Link>
                            ) : field.type === 'code' ? (
                              <code>{displayValue}</code>
                            ) : field.type === 'boolean' ? (
                              value ? 'Да' : 'Нет'
                            ) : (
                              displayValue
                            )}
                          </dd>
                        </div>
                      )
                    })}
                  </dl>
                </section>
              ))}
            </div>
          ) : null}
          
          {editing && EditForm ? (
            <EditForm
              entity={data}
              onSave={async (patch) => { await save(patch) }}
              onCancel={() => setEditing(false)}
            />
          ) : null}
        </>
      ) : null}
    </DetailPageShell>
  )
}
