export function exportRowsToCsv(
  rows: Array<Record<string, unknown> & { id: number }>,
  visibleColumnIds: string[],
  columnLabels: Record<string, string>,
  cellText: (row: any, colId: string) => string,
  filename: string,
): void {
  const esc = (s: string) => `"${s.replace(/"/g, '""')}"`
  
  const header = visibleColumnIds
    .map((id) => columnLabels[id] ?? id)
    .join(',')
  
  const lines = rows.map((row) =>
    visibleColumnIds
      .map((id) => esc(cellText(row, id)))
      .join(','),
  )
  
  const csv = [header, ...lines].join('\r\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `${filename}.csv`
  a.click()
  URL.revokeObjectURL(a.href)
}
