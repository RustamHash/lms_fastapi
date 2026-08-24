import { useState } from 'react'
import { createPortal } from 'react-dom'
import type { ListPreset } from '../hooks/useListPresets'
import type { TablePrefs } from '../hooks/useTableSettings'

type Props = {
  entityKey: string
  prefs: TablePrefs
  presets: ListPreset[]
  columnLabels: Record<string, string>
  availableFields?: { path: string; title: string }[]
  onApplyPrefs: (prefs: TablePrefs) => void
  onApplyPreset: (presetId: number) => Promise<void>
  onUpdatePreset: (presetId: number, name: string, config: TablePrefs) => Promise<unknown>
  onDeletePreset: (presetId: number) => Promise<void>
  onSetDefaultPreset: (presetId: number) => Promise<unknown>
  onResetToDefaults: () => Promise<void>
  onSavePreset: () => void
  onClose: () => void
}

type TabId = 'columns' | 'presets'

export function ListSettingsDialog({
  prefs,
  presets,
  columnLabels,
  availableFields = [],
  onApplyPrefs,
  onApplyPreset,
  onUpdatePreset,
  onDeletePreset,
  onSetDefaultPreset,
  onResetToDefaults,
  onSavePreset,
  onClose,
}: Props) {
  const [activeTab, setActiveTab] = useState<TabId>('columns')
  const [draftPrefs, setDraftPrefs] = useState<TablePrefs>({ ...prefs })
  const [applying, setApplying] = useState(false)
  const [activePresetId, setActivePresetId] = useState<number | null>(null)
  const [dragIndex, setDragIndex] = useState<number | null>(null)
  const [dropIndex, setDropIndex] = useState<number | null>(null)

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
    
    const newOrder = [...draftPrefs.order]
    const [moved] = newOrder.splice(dragIndex, 1)
    newOrder.splice(index, 0, moved)
    
    setDraftPrefs(prev => ({ ...prev, order: newOrder }))
    setDragIndex(null)
    setDropIndex(null)
  }

  function handleDragEnd() {
    setDragIndex(null)
    setDropIndex(null)
  }

  function toggleColumnVisibility(columnId: string) {
    setDraftPrefs(prev => {
      const isHidden = prev.hidden.includes(columnId)
      return {
        ...prev,
        hidden: isHidden
          ? prev.hidden.filter(id => id !== columnId)
          : [...prev.hidden, columnId]
      }
    })
  }

  async function handleApply() {
    setApplying(true)
    try {
      // Применяем к таблице
      onApplyPrefs({
        ...draftPrefs,
        order: draftPrefs.order,
        hidden: draftPrefs.hidden,
        widths: draftPrefs.widths,
      })
      
      // Если есть активный пресет — обновляем его
      if (activePresetId !== null) {
        const preset = presets.find(p => p.id === activePresetId)
        if (preset) {
          await onUpdatePreset(activePresetId, preset.name, draftPrefs)
        }
      }
      
      onClose()
    } finally {
      setApplying(false)
    }
  }

  async function handleReset() {
    setApplying(true)
    try {
      await onResetToDefaults()
      onClose()
    } finally {
      setApplying(false)
    }
  }

  return createPortal(
    <div className="dialog-backdrop" role="presentation">
      <div className="dialog dialog--wide" role="dialog" aria-modal="true" aria-labelledby="list-settings-title">
        <h3 id="list-settings-title" className="dialog__title">Настройка списка</h3>
        
        <div className="entity-tabs">

          <button
            type="button"
            className={`entity-tabs__btn${activeTab === 'columns' ? ' entity-tabs__btn--active' : ''}`}
            onClick={() => setActiveTab('columns')}
          >
            Колонки
          </button>

          <button
            type="button"
            className={`entity-tabs__btn${activeTab === 'presets' ? ' entity-tabs__btn--active' : ''}`}
            onClick={() => setActiveTab('presets')}
          >
            Пресеты
          </button>
        </div>



        {activeTab === 'columns' ? (
          <div className="list-settings-panel">
            <p className="dialog__hint">Перетащите для изменения порядка. Снимите галочку чтобы скрыть.</p>
            
            {/* Выбранные колонки */}
            <div className="list-settings-columns">
              {draftPrefs.order.map((columnId, index) => (
                <div
                  key={columnId}
                  className={`list-settings-column-item${dragIndex === index ? ' dragging' : ''}${dropIndex === index ? ' drop-over' : ''}`}
                  draggable
                  onDragStart={(e) => handleDragStart(index, e)}
                  onDragOver={(e) => handleDragOver(index, e)}
                  onDrop={(e) => handleDrop(index, e)}
                  onDragEnd={handleDragEnd}
                >
                  <span className="list-settings-column-item__handle" aria-hidden>⠿</span>
                  <label className="list-settings-filter-item">
                    <input
                      type="checkbox"
                      checked={!draftPrefs.hidden.includes(columnId)}
                      onChange={() => toggleColumnVisibility(columnId)}
                    />
                    {columnLabels[columnId] ?? columnId}
                  </label>
                </div>
              ))}
            </div>

            {/* Доступные поля (не выбранные) */}
            {availableFields.length > 0 ? (
              <>
                <p className="dialog__hint" style={{ marginTop: 16, fontWeight: 600 }}>
                  Доступные поля:
                </p>
                <div className="list-settings-available">
                  {availableFields
                    .filter((f) => !draftPrefs.order.includes(f.path))
                    .map((field) => (
                      <label
                        key={field.path}
                        className="list-settings-available-item"
                      >
                        <input
                          type="checkbox"
                          checked={false}
                          onChange={() => {
                            setDraftPrefs((prev) => ({
                              ...prev,
                              order: [...prev.order, field.path],
                              hidden: prev.hidden.filter((h) => h !== field.path),
                            }))
                          }}
                        />
                        <span>{field.title}</span>
                        <button
                          type="button"
                          className="list-settings-available-add"
                          onClick={() => {
                            setDraftPrefs((prev) => ({
                              ...prev,
                              order: [...prev.order, field.path],
                              hidden: prev.hidden.filter((h) => h !== field.path),
                            }))
                          }}
                          aria-label={`Добавить ${field.title}`}
                          title="Добавить колонку"
                        >
                          +
                        </button>
                      </label>
                    ))}
                </div>
              </>
            ) : null}
          </div>
        ) : null}



        {activeTab === 'presets' ? (
          <div className="list-settings-panel">
            <div className="list-settings-panel__header">
              <p className="dialog__hint">Сохранённые пресеты</p>
              <button
                type="button"
                className="tb tb--create"
                onClick={onSavePreset}
                title="Сохранить текущие настройки как пресет"
              >
                + Сохранить текущий
              </button>
            </div>
            {presets.length === 0 ? (
              <p className="list-msg list-msg--warn">Нет сохранённых пресетов</p>
            ) : (
              <div className="list-settings-presets">
                {presets.map(preset => (
                  <div key={preset.id} className="preset-item">
                    <div className="preset-item__info">
                      <span className="preset-item__name">
                        {preset.name}
                        {preset.is_default ? ' (по умолчанию)' : ''}
                      </span>
                    </div>
                    <div className="preset-item__actions">
                      <button
                        type="button"
                        className={`tb tb--create${activePresetId === preset.id ? ' tb--active-preset' : ''}`}
                        onClick={() => {
                          setActivePresetId(preset.id)
                          void onApplyPreset(preset.id)
                        }}
                        title={activePresetId === preset.id ? 'Активный пресет' : 'Сделать активным'}
                      >
                        {activePresetId === preset.id ? 'Активен' : 'Активировать'}
                      </button>
                      {!preset.is_default ? (
                        <button
                          type="button"
                          className="tb tb--view"
                          onClick={() => void onSetDefaultPreset(preset.id)}
                          title="По умолчанию"
                        >
                          По умолч.
                        </button>
                      ) : null}
                      <button
                        type="button"
                        className="tb tb--danger"
                        onClick={() => void onDeletePreset(preset.id)}
                        title="Удалить"
                      >
                        Удалить
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : null}

        <div className="dialog__actions">
          <button type="button" className="tb tb--create" onClick={handleApply} disabled={applying}>
            Применить
          </button>
          <button type="button" className="tb tb--reset" onClick={() => void handleReset()} disabled={applying}>
            Восстановить по умолчанию
          </button>
          <button type="button" className="tb tb--reset" onClick={onClose} data-close="true">
            Отмена
          </button>
        </div>
      </div>
    </div>,
    document.body
  )
}
