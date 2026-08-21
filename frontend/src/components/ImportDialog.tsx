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
  const [taskId, setTaskId] = useState<string | null>(null)
  const pollRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const logRef = useRef<HTMLDivElement>(null)

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearTimeout(pollRef.current)
      pollRef.current = null
    }
  }, [])

  useEffect(() => {
    return () => stopPolling()
  }, [stopPolling])

  // Автозапуск импорта при открытии окна (защита от двойного запуска)
  const startedRef = useRef(false)
  
  useEffect(() => {
    if (startedRef.current) return
    startedRef.current = true
    void handleImport()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Автопрокрутка лога вниз
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight
    }
  }, [allMessages, allErrors])

  async function downloadErrorsExcel() {
    const currentTaskId = status?.task_id ?? taskId
    if (!currentTaskId) return
    
    try {
      const token = sessionStorage.getItem('sslogistics_access_token')
      const res = await fetch(`/api/v1/integrations/import/${currentTaskId}/errors/excel`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        },
      })
      
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `import_errors_${currentTaskId}.xlsx`
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      console.error('Ошибка скачивания Excel:', e)
    }
  }

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
      
      if (!startData.task_id) {
        throw new Error('Не получен task_id от сервера')
      }
      
      setTaskId(startData.task_id)

      // 2. Long Polling — рекурсивный запрос
      const longPoll = async () => {
        if (!startData.task_id) return
        
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

            {/* Статистика — крупная, на всю ширину */}
            <div className="import-progress__stats">
              <div className="import-stat">
                <span className="import-stat__label">Всего</span>
                <span className="import-stat__value">{status.total_rows}</span>
              </div>
              <div className="import-stat">
                <span className="import-stat__label">Обработано</span>
                <span className="import-stat__value">{status.processed_rows}</span>
              </div>
              <div className="import-stat import-stat--success">
                <span className="import-stat__label">Успешно</span>
                <span className="import-stat__value">{status.success_rows}</span>
              </div>
              {status.error_rows > 0 ? (
                <div className="import-stat import-stat--error">
                  <span className="import-stat__label">Ошибок</span>
                  <span className="import-stat__value">{status.error_rows}</span>
                </div>
              ) : null}
              {status.order_number ? (
                <div className="import-stat import-stat--order">
                  <span className="import-stat__label">Заказ</span>
                  <span className="import-stat__value">{status.order_number}</span>
                </div>
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
          <div className="import-dialog-footer">
            <p className="import-progress__done">✅ Импорт завершён успешно</p>
            <button type="button" className="import-dialog-btn import-dialog-btn--primary" onClick={onClose} data-close="true">
              Закрыть
            </button>
          </div>
        ) : null}

        {isFailed || (isDone && status && status.error_rows > 0) ? (
          <div className="import-dialog-footer">
            <p className="import-progress__failed">❌ Импорт завершён с ошибками</p>
            <div className="import-dialog-footer__buttons">
              <button
                type="button"
                className="import-dialog-btn import-dialog-btn--error"
                onClick={() => void downloadErrorsExcel()}
              >
                Скачать Excel с ошибками
              </button>
              <button type="button" className="import-dialog-btn import-dialog-btn--primary" onClick={onClose} data-close="true">
                Закрыть
              </button>
            </div>
          </div>
        ) : null}

        {isRunning ? (
          <div className="import-dialog-footer">
            <p className="import-progress__running">⏳ Импорт выполняется...</p>
            <button type="button" className="import-dialog-btn import-dialog-btn--secondary" onClick={stopPolling}>
              Остановить опрос
            </button>
          </div>
        ) : null}
      </div>
    </div>,
    document.body
  )
}
