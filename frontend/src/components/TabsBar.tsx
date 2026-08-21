import { memo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTabs } from './TabsContext'

function TabsBarInner() {
  const { tabs, activePath, closeTab, closeAllTabs } = useTabs()
  const navigate = useNavigate()

  if (tabs.length === 0) return null

  return (
    <div className="tabs-bar">
      <div className="tabs-bar__tabs">
        {tabs.map((tab) => (
          <div
            key={tab.path}
            className={`tabs-bar__tab${tab.path === activePath ? ' tabs-bar__tab--active' : ''}`}
            onClick={() => navigate(tab.path)}
            title={tab.label}
          >
            <span className="tabs-bar__icon" aria-hidden>
              {tab.path === '/' ? '🏠' : '📄'}
            </span>
            <span className="tabs-bar__label">{tab.label}</span>
            <button
              type="button"
              className="tabs-bar__close"
              onClick={(e) => {
                e.stopPropagation()
                closeTab(tab.path)
              }}
              aria-label={`Закрыть ${tab.label}`}
              title="Закрыть"
            >
              ×
            </button>
          </div>
        ))}
      </div>
      {tabs.length > 1 ? (
        <button
          type="button"
          className="tabs-bar__close-all"
          onClick={closeAllTabs}
          title="Закрыть все вкладки"
        >
          ✕
        </button>
      ) : null}
    </div>
  )
}

export const TabsBar = memo(TabsBarInner)
