import { useEffect, useMemo, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { ListTableShell } from '../../components/ListTableShell'
import { TableCellContextMenu } from '../../components/TableCellContextMenu'
import { useAppNotice } from '../../notifications/AppNoticeContext'
import { useEntityList } from './useEntityList'
import type { ListPageConfig } from './types'

type ContextMenuState<Row> = {
  x: number
  y: number
  row: Row
  colId: string
}

type ColumnFilterDef =
  | { kind: 'text' }
  | { kind: 'datetime' }
  | { kind: 'select'; options: { value: string; label: string }[] }

function clampMenuPosition(x: number, y: number) {
  const menuW = 280
  const menuH = 72
  const pad = 8
  return {
    x: Math.max(pad, Math.min(x, window.innerWidth - menuW - pad)),
    y: Math.max(pad, Math.min(y, window.innerHeight - menuH - pad)),
  }
}

type Breadcrumb = { label: string; to?: string }

type Props<Row extends { id: number }> = {
  canCreate?: boolean
  onBack?: () => void

  breadcrumbs?: Breadcrumb[]
  config: ListPageConfig<Row>
}

export function EntityListPage<Row extends { id: number }>({ config, onBack, breadcrumbs, canCreate = true }: Props<Row>) {
  const navigate = useNavigate()
  const location = useLocation()
  const { notify } = useAppNotice()
  
  const entity = useEntityList(config)
  
  const [ctxMenu, setCtxMenu] = useState<ContextMenuState<Row> | null>(null)
  
  const [dialogOpen, setDialogOpen] = useState(false)
  const [draftOrder, setDraftOrder] = useState<string[]>([])
  const [draftHidden, setDraftHidden] = useState<Set<string>>(() => new Set())
  const [draftWidths, setDraftWidths] = useState<Record<string, string>>({})
  
  const columnMeta = useMemo(
    () => new Map(config.columns.map((c) => [c.id, c.label])),
    [config.columns],
  )
  
  const columnFilters = useMemo(() => {
    const map: Record<string, ColumnFilterDef> = {}
    for (const col of config.columns) {
      if (col.type === 'bool' || col.type === 'select') {
        map[col.id] = { kind: 'select', options: col.options ?? [] }
      } else if (col.type === 'date' || col.type === 'datetime') {
        map[col.id] = { kind: 'datetime' }
      } else {
        map[col.id] = { kind: 'text' }
      }
    }
    return map
  }, [config.columns])
  
  useEffect(() => {
    if (!ctxMenu) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setCtxMenu(null)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [ctxMenu])
  
  function openDialog() {
    setDraftOrder([...entity.prefs.order])
    setDraftHidden(new Set(entity.prefs.hidden))
    setDraftWidths(
      Object.fromEntries(
        entity.prefs.order.map((id) => [
          id,
          entity.prefs.widths[id] != null ? String(entity.prefs.widths[id]) : '',
        ]),
      ),
    )
    setDialogOpen(true)
  }
  
  async function saveDialog() {
    try {
      await entity.prefs.savePrefs({
        order: draftOrder,
        hidden: [...draftHidden],
        widths: Object.fromEntries(
          Object.entries(draftWidths)
            .filter(([_, v]) => v !== '')
            .map(([k, v]) => [k, Number(v)]),
        ),
      })
      setDialogOpen(false)
      notify('Настройки колонок сохранены', 'success')
    } catch {
      notify('Не удалось сохранить настройки колонок', 'error')
    }
  }
  
  function exportCsv() {
    const cols = entity.prefs.visibleOrderedIds
    const chosen = entity.rows.filter((r) => entity.selected.has(r.id))
    
    const esc = (s: string) => `"${s.replace(/"/g, '""')}"`
    const header = cols.map((id) => columnMeta.get(id) ?? id).join(',')
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
  }
  
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
  
  if (entity.error) {
    return (
      <section className="app-card app-card--wide">
        <h1 className="page-title">{config.title}</h1>
        <p className="list-msg list-msg--err" role="alert">
          Ошибка загрузки: {entity.error}
        </p>
      </section>
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
      
      <ListTableShell<Row>
        onRefresh={entity.reload}
        createHref={config.toolbar?.createHref}
        canCreate={canCreate}
        onExportCsv={exportCsv}
        onOpenView={openDialog}
        onResetFilters={entity.resetFilters}
        canOpenView={!entity.prefs.loading}
        hasActiveFilters={entity.hasActiveFilters}
        onNotify={notify}
        viewDialogOpen={dialogOpen}
        viewDialogTitle="Колонки таблицы"
        viewDialogHint="Порядок, видимость и ширина колонок сохраняются на сервере."
        viewDraftOrder={draftOrder}
        isViewDraftHidden={(id) => draftHidden.has(id)}
        onViewDraftToggle={(id, visible) => {
          setDraftHidden((prev) => {
            const next = new Set(prev)
            if (visible) next.delete(id)
            else next.add(id)
            return next
          })
        }}
        onViewDraftSelectAll={(visible) => {
          setDraftHidden(visible ? new Set() : new Set(draftOrder))
        }}
        onViewDraftSetOrder={setDraftOrder}
        viewDraftColumnWidth={(id) => draftWidths[id] ?? ''}
        onViewDraftColumnWidthChange={(id, value) =>
          setDraftWidths((prev) => ({ ...prev, [id]: value }))
        }
        onViewSave={() => void saveDialog()}
        onViewClose={() => setDialogOpen(false)}
        selectionCount={entity.selectedCount}
        visibleColumnIds={entity.prefs.visibleOrderedIds}
        columnLabel={(cid) => columnMeta.get(cid) ?? cid}
        sortCol={entity.sortCol}
        sortDir={entity.sortDir}
        onSortHeaderClick={entity.onSortHeaderClick}
        columnFilters={columnFilters}
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
          const newWidths = { ...entity.prefs.widths, [cid]: w }
          void entity.prefs.savePrefs({
            order: entity.prefs.order,
            hidden: entity.prefs.hidden,
            widths: newWidths,
          })
        }}
        plainCellText={entity.cellText}
      />
      
      {ctxMenu ? (
        <TableCellContextMenu
          x={ctxMenu.x}
          y={ctxMenu.y}
          canOpen={Boolean(ctxMenu.row.id)}
          onOpen={() => {
            const override = config.columnOverrides?.[ctxMenu.colId]
            if (override?.href) {
              navigate(override.href(ctxMenu.row), { state: location.state })
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
