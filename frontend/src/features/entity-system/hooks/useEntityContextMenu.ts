import { useCallback, useState } from 'react'
import type { MouseEvent } from 'react'

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

export function useEntityContextMenu<Row extends { id: number }>() {
  const [ctxMenu, setCtxMenu] = useState<ContextMenuState<Row> | null>(null)

  const onCellContextMenu = useCallback(
    (e: MouseEvent<HTMLTableCellElement>, row: Row, colId: string) => {
      e.preventDefault()
      const pos = clampMenuPosition(e.clientX, e.clientY)
      setCtxMenu({ x: pos.x, y: pos.y, row, colId })
    },
    [],
  )

  const closeContextMenu = useCallback(() => {
    setCtxMenu(null)
  }, [])

  return {
    ctxMenu,
    onCellContextMenu,
    closeContextMenu,
  }
}
