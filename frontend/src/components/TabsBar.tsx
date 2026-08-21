import { memo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTabs } from './TabsContext'

function TabsBarInner() {
  const { tabs, activePath, closeTab, closeAllTabs, moveTab } = useTabs()
  const navigate = useNavigate()
  const [dragIndex, setDragIndex] = useState<number | null>(null)
  const [dropIndex, setDropIndex] = useState<number | null>(null)

  if (tabs.length === 0) return null

  function handleDragStart(index: number, e: React.DragEvent) {
    setDragIndex(index)
    e.dataTransfer.effectAllowed = 'move'
  }

  function handleDragOver(index: number, e: React.DragEvent) {
    e.preventDefault()
    setDropIndex(index)
  }

  function handleDrop(index: number, e: React.DragEvent) {
    e.preventDefault()
    if (dragIndex === null || dragIndex === index) return
    moveTab(dragIndex, index)
    setDragIndex(null)
    setDropIndex(null)
  }

  function handleDragEnd() {
    setDragIndex(null)
    setDropIndex(null)
  }

  return (
    <div className="tabs-bar">
      <div className="tabs-bar__tabs">
        {tabs.map((tab, index) => (
          <div
            key={tab.path}
            className={`tabs-bar__tab${tab.path === activePath ? ' tabs-bar__tab--active' : ''}${dragIndex === index ? ' tabs-bar__tab--dragging' : ''}${dropIndex === index ? ' tabs-bar__tab--drop-over' : ''}`}
            onClick={() => navigate(tab.path)}
            title={tab.label}
            draggable
            onDragStart={(e) => handleDragStart(index, e)}
            onDragOver={(e) => handleDragOver(index, e)}
            onDrop={(e) => handleDrop(index, e)}
            onDragEnd={handleDragEnd}
          >
            <span className="tabs-bar__drag-handle" aria-hidden>⠿</span>
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
