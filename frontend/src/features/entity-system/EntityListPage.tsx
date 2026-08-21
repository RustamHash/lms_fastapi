import { useMemo, useState } from 'react'
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
import { useEntityFilters } from './hooks/useEntityFilters'
import { useEntityContextMenu } from './hooks/useEntityContextMenu'
import { exportRowsToCsv } from './exportCsv'
import type { ListPageConfig } from './types'

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

export function EntityListPage<Row extends { id: number }>({
  config,
  canCreate = true,
  onBack,
  breadcrumbs,
  onImport,
}: Props<Row>) {
  const navigate = useNavigate()
  const location = useLocation()
  const { notify } = useAppNotice()
  const entity = useEntityList(config)
  const filtersHook = useEntityFilters()
  const ctxMenuHook = useEntityContextMenu<Row>()
  
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [savePresetOpen, setSavePresetOpen] = useState(false)

  const columnFilters = useMemo(() => {
    return config.columns.reduce((acc, col) => {
      if (col.type === 'bool') {
        acc[col.id] = {
          kind: 'select' as const,
          options: [
            { value: 'true', label: 'Да' },
            { value: 'false', label: 'Нет' },
          ],
        }
      } else if (col.type === 'select') {
        acc[col.id] = { kind: 'select' as const, options: col.options ?? [] }
      } else if (col.type === 'date' || col.type === 'datetime') {
        acc[col.id] = { kind: 'datetime' as const }
      } else {
        acc[col.id] = { kind: 'text' as const }
      }
      return acc
    }, {} as Record<string, { kind: 'text' | 'select' | 'datetime'; options?: { value: string; label: string }[] }>)
  }, [config.columns])

  const columnLabels = useMemo(
    () => Object.fromEntries(config.columns.map(c => [c.id, c.label])),
    [config.columns],
  )

  function filterValueFromRow(row: Row, colId: string): string {
    const column = config.columns.find((c) => c.id === colId)
    if (!column) return entity.cellText(row, colId)
    
    if (column.type === 'bool') {
      return (row as unknown as Record<string, unknown>)[colId] ? 'true' : 'false'
    }
    return entity.cellText(row, colId)
  }

  function handleExportCsv() {
    const chosen = entity.rows.filter((r) => entity.selected.has(r.id))
    exportRowsToCsv(
      chosen,
      entity.prefs.visibleOrderedIds,
      columnLabels,
      entity.cellText,
      config.entityKey,
    )
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
          selectedRows={entity.rows.filter((r) => entity.selected.has(r.id))}
          context={{
            selectedRows: entity.rows.filter((r) => entity.selected.has(r.id)),
            selectedIds: Array.from(entity.selected),
            reload: entity.reload,
            clearSelection: entity.clearSelection,
            notify,
          }}
        />
      ) : null}
      
      <QuickFiltersBar
        quickFilters={filtersHook.quickFilters}
        filters={filtersHook.filters}
        columnFilters={columnFilters}
        columnLabel={(cid) => columnLabels[cid] ?? cid}
        onFilterChange={filtersHook.setFilter}
      />

      <ListTableShell<Row>
        filtersBar={
          <ActiveFiltersBar
            prefs={{
              order: entity.prefs.order,
              hidden: entity.prefs.hidden,
              widths: entity.prefs.widths,
              filters: filtersHook.filters,
              exclude_filters: filtersHook.excludeFilters,
              sort: entity.sortCol ? { column: entity.sortCol, direction: entity.sortDir } : null,
              quick_filters: filtersHook.quickFilters,
            }}
            columnLabel={(cid) => columnLabels[cid] ?? cid}
            onRemoveFilter={(cid) => filtersHook.setFilter(cid, '')}
            onRemoveExclude={filtersHook.removeExcludeFilter}
          />
        }
        onRefresh={entity.reload}
        createHref={config.toolbar?.createHref}
        canCreate={canCreate}
        onExportCsv={handleExportCsv}
        onOpenView={() => setSettingsOpen(true)}
        onResetFilters={filtersHook.resetFilters}
        canOpenView={!entity.prefs.loading}
        hasActiveFilters={filtersHook.hasActiveFilters}
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
        columnLabel={(cid) => columnLabels[cid] ?? cid}
        sortCol={entity.sortCol}
        sortDir={entity.sortDir}
        onSortHeaderClick={entity.onSortHeaderClick}
        columnFilters={columnFilters}
        filters={filtersHook.filters}
        excludeFilters={filtersHook.excludeFilters}
        onFilterChange={filtersHook.setFilter}
        loading={entity.loading}
        rows={entity.rows}
        allSelected={entity.allSelected}
        onToggleAll={entity.toggleAll}
        isSelected={(id) => entity.selected.has(id)}
        onToggleRow={entity.toggleRow}
        onCellContextMenu={ctxMenuHook.onCellContextMenu}
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
        onInvertSelection={() => entity.toggleAll(!entity.allSelected)}
        onRowDoubleClick={(row) => {
          const linkColumn = config.columns.find(col => config.columnOverrides?.[col.id]?.href)
          if (linkColumn) {
            const href = config.columnOverrides?.[linkColumn.id]?.href
            if (href) {
              navigate(href(row), { state: location.state })
              return
            }
          }
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
            filters: filtersHook.filters,
            exclude_filters: filtersHook.excludeFilters,
            sort: entity.sortCol ? { column: entity.sortCol, direction: entity.sortDir } : null,
            quick_filters: filtersHook.quickFilters,
          }}
          presets={entity.listPresets.presets}
          columnLabels={columnLabels}
          onApplyPrefs={(prefs) => {
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
            await entity.listPresets.applyPreset(presetId)
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
            filters: filtersHook.filters,
            exclude_filters: filtersHook.excludeFilters,
            sort: entity.sortCol ? { column: entity.sortCol, direction: entity.sortDir } : null,
            quick_filters: filtersHook.quickFilters,
          }}
          onSave={async (name, config, isDefault) => {
            await entity.listPresets.createPreset(name, config, isDefault)
            notify('Пресет сохранён', 'success')
          }}
          onClose={() => setSavePresetOpen(false)}
        />
      ) : null}

      {ctxMenuHook.ctxMenu ? (
        <TableCellContextMenu
          x={ctxMenuHook.ctxMenu.x}
          y={ctxMenuHook.ctxMenu.y}
          canOpen={Boolean(ctxMenuHook.ctxMenu.row.id)}
          onOpen={() => {
            const override = config.columnOverrides?.[ctxMenuHook.ctxMenu.colId]
            if (override?.href) {
              navigate(override.href(ctxMenuHook.ctxMenu.row), { state: location.state })
            }
          }}
          onOpenInNewTab={() => {
            const override = config.columnOverrides?.[ctxMenuHook.ctxMenu.colId]
            if (override?.href) {
              window.open(override.href(ctxMenuHook.ctxMenu.row), '_blank', 'noopener,noreferrer')
            }
          }}
          onFilterByValue={() => {
            const val = filterValueFromRow(ctxMenuHook.ctxMenu.row, ctxMenuHook.ctxMenu.colId)
            filtersHook.setFilter(ctxMenuHook.ctxMenu.colId, val)
            ctxMenuHook.closeContextMenu()
          }}
          onExcludeValue={() => {
            const val = filterValueFromRow(ctxMenuHook.ctxMenu.row, ctxMenuHook.ctxMenu.colId)
            filtersHook.setExcludeFilter(ctxMenuHook.ctxMenu.colId, val)
            ctxMenuHook.closeContextMenu()
          }}
          canResetColumn={
            Boolean(filtersHook.filters[ctxMenuHook.ctxMenu.colId]) ||
            (filtersHook.excludeFilters[ctxMenuHook.ctxMenu.colId]?.length ?? 0) > 0
          }
          onResetColumnFilter={() => {
            filtersHook.resetColumnFilter(ctxMenuHook.ctxMenu.colId)
            ctxMenuHook.closeContextMenu()
          }}
          canResetAll={filtersHook.hasActiveFilters}
          onResetAllFilters={() => {
            filtersHook.resetFilters()
            ctxMenuHook.closeContextMenu()
          }}
          onClose={ctxMenuHook.closeContextMenu}
        />
      ) : null}
    </section>
  )
}
