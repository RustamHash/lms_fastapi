import { useState } from 'react'
import type { ListPreset } from '../hooks/useListPresets'
import type { TablePrefs } from '../hooks/useTableSettings'

type Props = {
  entityKey: string
  prefs: TablePrefs
  presets: ListPreset[]
  columnLabels: Record<string, string>
  allColumns: string[]
  onApplyPrefs: (prefs: TablePrefs) => void
  onApplyPreset: (presetId: number) => Promise<void>
  onDeletePreset: (presetId: number) => Promise<void>
  onSetDefaultPreset: (presetId: number) => Promise<unknown>
  onResetToDefaults: () => Promise<void>
  onClose: () => void
}

type TabId = 'filters' | 'columns' | 'sort' | 'presets'

export function ListSettingsDialog({
  prefs,
  presets,
  columnLabels,
  allColumns,
  onApplyPrefs,
  onApplyPreset,
  onDeletePreset,
  onSetDefaultPreset,
  onResetToDefaults,
  onClose,
}: Props) {
  const [activeTab, setActiveTab] = useState<TabId>('filters')
  const [draftPrefs, setDraftPrefs] = useState<TablePrefs>({ ...prefs })
  const [applying, setApplying] = useState(false)

  function toggleQuickFilter(columnId: string) {
    setDraftPrefs(prev => {
      const isIncluded = prev.quick_filters.includes(columnId)
      return {
        ...prev,
        quick_filters: isIncluded
          ? prev.quick_filters.filter(id => id !== columnId)
          : [...prev.quick_filters, columnId]
      }
    })
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

  function handleApply() {
    setApplying(true)
    onApplyPrefs(draftPrefs)
    onClose()
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

  return (
    <div className="dialog-backdrop" role="presentation">
      <div className="dialog dialog--wide" role="dialog" aria-modal="true" aria-labelledby="list-settings-title">
        <h3 id="list-settings-title" className="dialog__title">Настройка списка</h3>
        
        <div className="entity-tabs">
          <button
            type="button"
            className={`entity-tabs__btn${activeTab === 'filters' ? ' entity-tabs__btn--active' : ''}`}
            onClick={() => setActiveTab('filters')}
          >
            Фильтры
          </button>
          <button
            type="button"
            className={`entity-tabs__btn${activeTab === 'columns' ? ' entity-tabs__btn--active' : ''}`}
            onClick={() => setActiveTab('columns')}
          >
            Колонки
          </button>
          <button
            type="button"
            className={`entity-tabs__btn${activeTab === 'sort' ? ' entity-tabs__btn--active' : ''}`}
            onClick={() => setActiveTab('sort')}
          >
            Сортировка
          </button>
          <button
            type="button"
            className={`entity-tabs__btn${activeTab === 'presets' ? ' entity-tabs__btn--active' : ''}`}
            onClick={() => setActiveTab('presets')}
          >
            Пресеты
          </button>
        </div>

        {activeTab === 'filters' ? (
          <div className="list-settings-panel">
            <p className="dialog__hint">Выберите фильтры для отображения в шапке</p>
            <div className="list-settings-filters">
              {allColumns.map(columnId => (
                <label key={columnId} className="list-settings-filter-item">
                  <input
                    type="checkbox"
                    checked={draftPrefs.quick_filters.includes(columnId)}
                    onChange={() => toggleQuickFilter(columnId)}
                  />
                  {columnLabels[columnId] ?? columnId}
                </label>
              ))}
            </div>
          </div>
        ) : null}

        {activeTab === 'columns' ? (
          <div className="list-settings-panel">
            <p className="dialog__hint">Выберите видимые колонки</p>
            <div className="list-settings-columns">
              {allColumns.map(columnId => (
                <label key={columnId} className="list-settings-filter-item">
                  <input
                    type="checkbox"
                    checked={!draftPrefs.hidden.includes(columnId)}
                    onChange={() => toggleColumnVisibility(columnId)}
                  />
                  {columnLabels[columnId] ?? columnId}
                </label>
              ))}
            </div>
          </div>
        ) : null}

        {activeTab === 'sort' ? (
          <div className="list-settings-panel">
            <p className="dialog__hint">Настройте сортировку</p>
            <div className="wh-form">
              <label>
                Колонка
                <select
                  value={draftPrefs.sort?.column ?? ''}
                  onChange={(e) => setDraftPrefs(prev => ({
                    ...prev,
                    sort: e.target.value
                      ? { column: e.target.value, direction: prev.sort?.direction ?? 'asc' }
                      : null
                  }))}
                >
                  <option value="">Не сортировать</option>
                  {allColumns.map(columnId => (
                    <option key={columnId} value={columnId}>
                      {columnLabels[columnId] ?? columnId}
                    </option>
                  ))}
                </select>
              </label>
              {draftPrefs.sort ? (
                <label>
                  Направление
                  <select
                    value={draftPrefs.sort.direction}
                    onChange={(e) => setDraftPrefs(prev => ({
                      ...prev,
                      sort: { column: prev.sort?.column ?? '', direction: e.target.value as 'asc' | 'desc' }
                    }))}
                  >
                    <option value="asc">По возрастанию</option>
                    <option value="desc">По убыванию</option>
                  </select>
                </label>
              ) : null}
            </div>
          </div>
        ) : null}

        {activeTab === 'presets' ? (
          <div className="list-settings-panel">
            <p className="dialog__hint">Сохранённые пресеты</p>
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
                        className="tb tb--create"
                        onClick={() => void onApplyPreset(preset.id)}
                        title="Применить"
                      >
                        Применить
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
          <button type="button" className="tb tb--reset" onClick={onClose}>
            Отмена
          </button>
        </div>
      </div>
    </div>
  )
}
