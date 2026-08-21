import { useCallback, useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { apiFetch } from '../lib/http'

type Props = {
  documentType: 'porder' | 'order' | 'all'
  title: string
  onClose: () => void
}

type ImportStatus = {
  task_id: string
  status: 'starting' | 'processing' | 'completed' | 'failed'
  total_rows: number
  processed_rows: number
  success_rows: number
  error_rows: number
  messages: string[]
  errors: string[]
  order_number: string | null
}

export function ImportDialog({ documentType, title, onClose }: Props) {
  const [status, setStatus] = useState<ImportStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [allMessages, setAllMessages] = useState<string[]>([])
  const [allErrors, setAllErrors] = useState<string[]>([])
  const pollRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const logRef = useRef<HTMLDivElement>(null)

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current)
      pollRef.current = null
    }
  }, [])

  useEffect(() => {
    return () => stopPolling()
  }, [stopPolling])

  // Автозапуск импорта при открытии окна
  useEffect(() => {
    void handleImport()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Автопрокрутка лога вниз
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight
    }
  }, [allMessages, allErrors])

  async function handleImport() {
    setError(null)
    setStatus(null)

    try {
      // 1. Запускаем импорт
      const startRes = await apiFetch('/api/v1/integrations/import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(documentType === 'all' ? {} : { document_type: documentType }),
      })

      if (!startRes.ok) {
        const data = await startRes.json().catch(() => null)
        throw new Error(data?.detail ?? `HTTP ${startRes.status}`)
      }

      const startData = await startRes.json() as { task_id: string; log_id: number; status: string }

      // 2. Long Polling — рекурсивный запрос
      const longPoll = async () => {
        try {
          const statusRes = await apiFetch(`/api/v1/integrations/import/${startData.task_id}/status/long`)
          if (!statusRes.ok) throw new Error(`HTTP ${statusRes.status}`)

          const statusData = await statusRes.json() as ImportStatus
          setStatus(statusData)

          // Добавляем только новые сообщения
          setAllMessages(prev => {
            const newMessages = statusData.messages.filter(msg => !prev.includes(msg))
            return [...prev, ...newMessages]
          })

          setAllErrors(prev => {
            const newErrors = statusData.errors.filter(err => !prev.includes(err))
            return [...prev, ...newErrors]
          })

          if (statusData.status === 'completed' || statusData.status === 'failed') {
            stopPolling()
            return
          }

          // Сразу делаем новый Long Polling запрос
          pollRef.current = setTimeout(() => {
            void longPoll()
          }, 100)
        } catch (e) {
          console.error('Ошибка Long Polling:', e)
          // При ошибке — пробуем снова через 2 секунды
          pollRef.current = setTimeout(() => {
            void longPoll()
          }, 2000)
        }
      }

      // Запускаем Long Polling
      void longPoll()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка импорта')
      stopPolling()
    }
  }

  const isRunning = status?.status === 'starting' || status?.status === 'processing'
  const isDone = status?.status === 'completed'
  const isFailed = status?.status === 'failed'

  return createPortal(
    <div className="dialog-backdrop" role="presentation">
      <div className="dialog dialog--wide" role="dialog" aria-modal="true" aria-labelledby="import-title">
        <h3 id="import-title" className="dialog__title">{title}</h3>

        <div className="dialog__text">
          {documentType === 'porder' ? (
            <p className="dialog__hint">Импорт приходных заказов (porder).</p>
          ) : documentType === 'order' ? (
            <p className="dialog__hint">Импорт расходных заказов (order).</p>
          ) : (
            <p className="dialog__hint">Импорт всех типов заказов.</p>
          )}
        </div>



        {error ? (
          <p className="list-msg list-msg--err" role="alert">{error}</p>
        ) : null}

        {status ? (
          <div className="import-progress">
            {/* Текущий шаг */}
            {allMessages.length > 0 ? (
              <div className="import-progress__current-step">
                {allMessages[allMessages.length - 1]}
              </div>
            ) : null}

            {/* Прогресс-бар */}
            {status.total_rows > 0 ? (
              <div className="import-progress__bar">
                <div
                  className="import-progress__fill"
                  style={{ width: `${(status.processed_rows / status.total_rows) * 100}%` }}
                />
              </div>
            ) : null}

            {/* Статистика */}
            <div className="import-progress__stats">
              <span>Всего: {status.total_rows}</span>
              <span>Обработано: {status.processed_rows}</span>
              <span className="import-progress__success">Успешно: {status.success_rows}</span>
              {status.error_rows > 0 ? (
                <span className="import-progress__error">Ошибок: {status.error_rows}</span>
              ) : null}
              {status.order_number ? (
                <span>Заказ: {status.order_number}</span>
              ) : null}
            </div>

            {/* Лог */}
            <div className="import-progress__log" ref={logRef}>
              {allMessages.map((msg, index) => (
                <div key={index} className="import-progress__log-line">
                  {msg}
                </div>
              ))}
              {allErrors.map((err, index) => (
                <div key={`err-${index}`} className="import-progress__log-line import-progress__log-line--error">
                  ❌ {err}
                </div>
              ))}
            </div>
          </div>
        ) : null}

        {/* Кнопки в конце */}
        {isDone ? (
          <div className="dialog__actions">
            <p className="import-progress__done">✅ Импорт завершён успешно</p>
            <button type="button" className="tb tb--reset" onClick={onClose} data-close="true">
              Закрыть
            </button>
          </div>
        ) : null}

        {isFailed ? (
          <div className="dialog__actions">
            <p className="import-progress__failed">❌ Импорт завершён с ошибками</p>
            <button type="button" className="tb tb--reset" onClick={onClose} data-close="true">
              Закрыть
            </button>
          </div>
        ) : null}

        {isRunning ? (
          <div className="dialog__actions">
            <p className="import-progress__running">⏳ Импорт выполняется...</p>
            <button type="button" className="tb tb--reset" onClick={stopPolling}>
              Остановить опрос
            </button>
          </div>
        ) : null}
      </div>
    </div>,
    document.body
  )
}
