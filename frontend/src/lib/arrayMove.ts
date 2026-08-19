/** Перемещает элемент с индекса `from` на позицию `to` (как в dnd-kit arrayMove). */
export function arrayMove<T>(list: T[], from: number, to: number): T[] {
  if (from === to || from < 0 || to < 0 || from >= list.length || to >= list.length) {
    return [...list]
  }
  const next = [...list]
  const [item] = next.splice(from, 1)
  if (item === undefined) return [...list]
  next.splice(to, 0, item)
  return next
}
