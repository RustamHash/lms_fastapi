import { useCallback, useMemo, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { ListTableShell } from '../../components/ListTableShell'
import { TableCellContextMenu } from '../../components/TableCellContextMenu'
import { useAppNotice } from '../../notifications/AppNoticeContext'
import { GroupActionsBar } from './GroupActionsBar'
import { ActiveFiltersBar } from '../../components/ActiveFiltersBar'
import { QuickFiltersBar } from '../../components/QuickFiltersBar'
import { ListSettingsDialog } from '../../components/ListSettingsDialog'
import { SavePresetDialog } from '../../components/SavePresetDialog'
import { useEntityList } from './hooks/useEntityList'
import type { GroupActionContext, ListPageConfig, RowAction } from './types'

type ContextMenuState<Row> = {
  x: number
  y: number
  row: Row
  colId: string
}

function clampMenuPosition(x: number, y: number) {
  const menuW = 280
  const menuH = 72
  const pad = 8
  return {
    x: Math.max(pad, Math.min(x, window.innerWidth - menuW - pad)),
    y: Math.max(pad, Math.min(y, window.innerHeight - menuH - pad)),
  }
}

type Breadcrumb = {
  label: string
  to?: string
}

type Props<Row extends { id: number }> = {
  config: ListPageConfig<Row>
  canCreate?: boolean
  onBack?: () => void
  breadcrumbs?: Breadcrumb[]
  onImport?: () => void
}

export function EntityListPage<Row extends { id: number }>({ config, onBack, breadcrumbs, canCreate = true, onImport }: Props<Row>) {
  const navigate = useNavigate()
  const location = useLocation()
  const { notify } = useAppNotice()
  const entity = useEntityList(config)
  
  const [ctxMenu, setCtxMenu] = useState<ContextMenuState<Row> | null>(null)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [savePresetOpen, setSavePresetOpen] = useState(false)
  
  const groupActionContext: GroupActionContext<Row> = useMemo(() => ({
    selectedRows: entity.rows.filter((r) => entity.selected.has(r.id)),
    selectedIds: Array.from(entity.selected),
    reload: entity.reload,
    clearSelection: entity.clearSelection,
    notify,
  }), [entity.rows, entity.selected, entity.reload, entity.clearSelection, notify])
  
  const executeRowAction = useCallback(async (action: RowAction<Row>, row: Row) => {
    if (action.href) {
      navigate(action.href(row))
      return
    }
    
    if (action.action) {
      if (action.confirmMessage) {
        const message = typeof action.confirmMessage === 'function'
          ? action.confirmMessage(row)
          : action.confirmMessage
        
        if (!window.confirm(message)) return
      }
      
      await action.action(row, groupActionContext)
    }
  }, [navigate, groupActionContext])
  
  function onCellContextMenu(e: React.MouseEvent, row: Row, colId: string) {
    e.preventDefault()
    const pos = clampMenuPosition(e.clientX, e.clientY)
    setCtxMenu({ x: pos.x, y: pos.y, row, colId })
  }
  
  function filterValueFromRow(row: Row, colId: string): string {
    const column = config.columns.find((c) => c.id === colId)
    if (!column) return entity.cellText(row, colId)
    
    if (column.type === 'bool') {
      return (row as unknown as Record<string, unknown>)[colId] ? 'true' : 'false'
    }
    return entity.cellText(row, colId)
  }
  
  return (
    <section className="app-card app-card--wide list-page-shell">
      <div className="detail-nav">
        {onBack ? (
          <button type="button" className="detail-nav__back" onClick={onBack}>
            ← Назад
          </button>
        ) : null}
        {breadcrumbs && breadcrumbs.length > 0 ? (
          <nav className="breadcrumbs" aria-label="Хлебные крошки">
            {breadcrumbs.map((crumb, index) => (
              <span key={index} className="breadcrumbs__item">
                {crumb.to ? (
                  <Link to={crumb.to} className="breadcrumbs__link">
                    {crumb.label}
                  </Link>
                ) : (
                  <span className="breadcrumbs__current">{crumb.label}</span>
                )}
                {index < breadcrumbs.length - 1 ? (
                  <span className="breadcrumbs__sep">/</span>
                ) : null}
              </span>
            ))}
          </nav>
        ) : null}
      </div>

      <div className="list-page-header">
        <div className="list-page-header__info">
          <h1 className="page-title list-page-header__title">{config.title}</h1>
          {config.subtitle ? (
            <p className="list-page-header__subtitle">{config.subtitle}</p>
          ) : null}
        </div>
      </div>
      
      {config.groupActions && entity.selectedCount > 0 ? (
        <GroupActionsBar
          actions={config.groupActions}
          selectedRows={groupActionContext.selectedRows}
          context={groupActionContext}
        />
      ) : null}
      
      <QuickFiltersBar
        quickFilters={entity.quickFilters}
        filters={entity.filters}
        columnFilters={config.columns.reduce((acc, col) => {
          if (col.type === 'bool') {
            acc[col.id] = {
              kind: 'select',
              options: [
                { value: 'true', label: 'Да' },
                { value: 'false', label: 'Нет' },
              ],
            }
          } else if (col.type === 'select') {
            acc[col.id] = { kind: 'select', options: col.options ?? [] }
          } else if (col.type === 'date' || col.type === 'datetime') {
            acc[col.id] = { kind: 'datetime' }
          } else {
            acc[col.id] = { kind: 'text' }
          }
          return acc
        }, {} as Record<string, any>)}
        columnLabel={(cid) => config.columns.find((c) => c.id === cid)?.label ?? cid}
        onFilterChange={(cid, next) => {
          entity.setFilters((prev) => {
            if (next === '') {
              const { [cid]: _, ...rest } = prev
              return rest
            }
            return { ...prev, [cid]: next }
          })
        }}
      />

      <ListTableShell<Row>
        filtersBar={
          <ActiveFiltersBar
            prefs={{
              order: entity.prefs.order,
              hidden: entity.prefs.hidden,
              widths: entity.prefs.widths,
              filters: entity.filters,
              exclude_filters: entity.excludeFilters,
              sort: entity.sortCol ? { column: entity.sortCol, direction: entity.sortDir } : null,
              quick_filters: entity.quickFilters,
            }}
            columnLabel={(cid) => config.columns.find((c) => c.id === cid)?.label ?? cid}
            onRemoveFilter={(cid) => {
              entity.setFilters((prev) => {
                const next = { ...prev }
                delete next[cid]
                return next
              })
            }}
            onRemoveExclude={(cid, value) => {
              entity.setExcludeFilters((prev) => {
                const cur = prev[cid] ?? []
                return { ...prev, [cid]: cur.filter(v => v !== value) }
              })
            }}
          />
        }
        onRefresh={entity.reload}
        createHref={config.toolbar?.createHref}
        canCreate={canCreate}
        onExportCsv={() => {
          const cols = entity.prefs.visibleOrderedIds
          const chosen = entity.rows.filter((r) => entity.selected.has(r.id))
          const esc = (s: string) => `"${s.replace(/"/g, '""')}"`
          const header = cols.map((id) => {
            const col = config.columns.find((c) => c.id === id)
            return col?.label ?? id
          }).join(',')
          const lines = chosen.map((row) =>
            cols.map((id) => esc(entity.cellText(row, id))).join(','),
          )
          const csv = [header, ...lines].join('\r\n')
          const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
          const a = document.createElement('a')
          a.href = URL.createObjectURL(blob)
          a.download = `${config.entityKey}.csv`
          a.click()
          URL.revokeObjectURL(a.href)
        }}
        onOpenView={() => setSettingsOpen(true)}
        onResetFilters={entity.resetFilters}
        canOpenView={!entity.prefs.loading}
        hasActiveFilters={entity.hasActiveFilters}
        onNotify={notify}
        viewDialogOpen={false}
        viewDialogTitle=""
        viewDialogHint=""
        viewDraftOrder={[]}
        isViewDraftHidden={() => false}
        onViewDraftToggle={() => {}}
        onViewDraftSelectAll={() => {}}
        onViewDraftSetOrder={() => {}}
        viewDraftColumnWidth={() => ''}
        onViewDraftColumnWidthChange={() => {}}
        onViewSave={() => {}}
        onViewClose={() => {}}
        selectionCount={entity.selectedCount}
        visibleColumnIds={entity.prefs.visibleOrderedIds}
        columnLabel={(cid) => config.columns.find((c) => c.id === cid)?.label ?? cid}
        sortCol={entity.sortCol}
        sortDir={entity.sortDir}
        onSortHeaderClick={entity.onSortHeaderClick}
        columnFilters={config.columns.reduce((acc, col) => {
          if (col.type === 'bool') {
            acc[col.id] = {
              kind: 'select',
              options: [
                { value: 'true', label: 'Да' },
                { value: 'false', label: 'Нет' },
              ],
            }
          } else if (col.type === 'select') {
            acc[col.id] = { kind: 'select', options: col.options ?? [] }
          } else if (col.type === 'date' || col.type === 'datetime') {
            acc[col.id] = { kind: 'datetime' }
          } else {
            acc[col.id] = { kind: 'text' }
          }
          return acc
        }, {} as Record<string, any>)}
        filters={entity.filters}
        excludeFilters={entity.excludeFilters}
        onFilterChange={(cid, next) => {
          entity.setFilters((prev) => {
            if (next === '') {
              const { [cid]: _, ...rest } = prev
              return rest
            }
            return { ...prev, [cid]: next }
          })
        }}
        loading={entity.loading}
        rows={entity.rows}
        allSelected={entity.allSelected}
        onToggleAll={entity.toggleAll}
        isSelected={(id) => entity.selected.has(id)}
        onToggleRow={entity.toggleRow}
        onCellContextMenu={onCellContextMenu}
        renderCell={entity.renderCell}
        totalRowsCount={entity.totalRowsCount}
        columnWidthsPx={entity.prefs.widths}
        onCommitColumnWidth={(cid, w) => {
          void entity.prefs.savePrefs({
            order: entity.prefs.order,
            hidden: entity.prefs.hidden,
            widths: { ...entity.prefs.widths, [cid]: w },
          })
        }}
        plainCellText={entity.cellText}
        onImport={onImport}
        onInvertSelection={() => {
          entity.toggleAll(!entity.allSelected)
        }}
        onRowDoubleClick={(row) => {
          // Ищем колонку с href
          const linkColumn = config.columns.find(col => config.columnOverrides?.[col.id]?.href)
          if (linkColumn) {
            const href = config.columnOverrides?.[linkColumn.id]?.href
            if (href) {
              navigate(href(row), { state: location.state })
              return
            }
          }
          
          // Если href нет - показываем уведомление
          notify('Нет детальной страницы для этой записи', 'info')
        }}
      />
      
      {settingsOpen ? (
        <ListSettingsDialog
          entityKey={config.entityKey}
          prefs={{
            order: entity.prefs.order,
            hidden: entity.prefs.hidden,
            widths: entity.prefs.widths,
            filters: entity.filters,
            exclude_filters: entity.excludeFilters,
            sort: entity.sortCol ? { column: entity.sortCol, direction: entity.sortDir } : null,
            quick_filters: entity.quickFilters,
          }}
          presets={entity.listPresets.presets}
          columnLabels={Object.fromEntries(config.columns.map(c => [c.id, c.label]))}
          onApplyPrefs={(prefs) => {
            entity.setFilters(prefs.filters)
            entity.setExcludeFilters(prefs.exclude_filters)
            entity.setQuickFilters(prefs.quick_filters)
            
            // Сохраняем колонки
            void entity.prefs.savePrefs({
              order: prefs.order,
              hidden: prefs.hidden,
              widths: prefs.widths,
              filters: prefs.filters,
              exclude_filters: prefs.exclude_filters,
              sort: prefs.sort,
              quick_filters: prefs.quick_filters,
            })
          }}
          onApplyPreset={async (presetId) => {
            const prefs = await entity.listPresets.applyPreset(presetId)
            entity.setFilters(prefs.filters)
            entity.setExcludeFilters(prefs.exclude_filters)
            entity.setQuickFilters(prefs.quick_filters)
          }}
          onUpdatePreset={entity.listPresets.updatePreset}
          onDeletePreset={entity.listPresets.deletePreset}
          onSetDefaultPreset={entity.listPresets.setDefaultPreset}
          onResetToDefaults={entity.resetToDefaults}
          onSavePreset={() => setSavePresetOpen(true)}
          onClose={() => setSettingsOpen(false)}
        />
      ) : null}

      {savePresetOpen ? (
        <SavePresetDialog
          entityKey={config.entityKey}
          currentPrefs={{
            order: entity.prefs.order,
            hidden: entity.prefs.hidden,
            widths: entity.prefs.widths,
            filters: entity.filters,
            exclude_filters: entity.excludeFilters,
            sort: entity.sortCol ? { column: entity.sortCol, direction: entity.sortDir } : null,
            quick_filters: entity.quickFilters,
          }}
          onSave={async (name, config, isDefault) => {
            await entity.listPresets.createPreset(name, config, isDefault)
            notify('Пресет сохранён', 'success')
          }}
          onClose={() => setSavePresetOpen(false)}
        />
      ) : null}

      {ctxMenu ? (
        <TableCellContextMenu
          x={ctxMenu.x}
          y={ctxMenu.y}
          canOpen={Boolean(ctxMenu.row.id)}
          onOpen={() => {
            const override = config.columnOverrides?.[ctxMenu.colId]
            if (override?.href) {
              navigate(override.href(ctxMenu.row), { state: location.state })
            } else if (config.rowActions?.find((a) => a.id === 'edit')) {
              const editAction = config.rowActions.find((a) => a.id === 'edit')!
              void executeRowAction(editAction, ctxMenu.row)
            }
          }}
          onOpenInNewTab={() => {
            const override = config.columnOverrides?.[ctxMenu.colId]
            if (override?.href) {
              window.open(override.href(ctxMenu.row), '_blank', 'noopener,noreferrer')
            }
          }}
          onFilterByValue={() => {
            const val = filterValueFromRow(ctxMenu.row, ctxMenu.colId)
            entity.setFilters((prev) => ({ ...prev, [ctxMenu.colId]: val }))
            setCtxMenu(null)
          }}
          onExcludeValue={() => {
            const val = filterValueFromRow(ctxMenu.row, ctxMenu.colId)
            entity.setExcludeFilters((prev) => {
              const cur = prev[ctxMenu.colId] ?? []
              if (cur.includes(val)) return prev
              return { ...prev, [ctxMenu.colId]: [...cur, val] }
            })
            setCtxMenu(null)
          }}
          canResetColumn={
            Boolean(entity.filters[ctxMenu.colId]) ||
            (entity.excludeFilters[ctxMenu.colId]?.length ?? 0) > 0
          }
          onResetColumnFilter={() => {
            entity.setFilters((prev) => {
              const next = { ...prev }
              delete next[ctxMenu.colId]
              return next
            })
            entity.setExcludeFilters((prev) => {
              const next = { ...prev }
              delete next[ctxMenu.colId]
              return next
            })
          }}
          canResetAll={entity.hasActiveFilters}
          onResetAllFilters={entity.resetFilters}
          onClose={() => setCtxMenu(null)}
        />
      ) : null}
    </section>
  )
}
