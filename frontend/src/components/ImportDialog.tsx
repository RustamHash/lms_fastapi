import { useCallback, useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { apiClient } from '../lib/apiClient'

type Props = {
  documentType: 'porder' | 'order' | 'all'
  title: string
  onClose: () => void
  /** Вызывается при завершении импорта (success/failed), чтобы обновить список на странице. */
  onSuccess?: () => void
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
  current_step: string
  order_number: string | null
}

export function ImportDialog({ documentType, title, onClose, onSuccess }: Props) {
  const documentTypeRef = useRef(documentType)
  const onSuccessRef = useRef(onSuccess)
  const listNotifiedRef = useRef(false)

  useEffect(() => {
    documentTypeRef.current = documentType
  }, [documentType])

  useEffect(() => {
    onSuccessRef.current = onSuccess
  }, [onSuccess])

  const notifyList = useCallback(() => {
    if (listNotifiedRef.current) return
    listNotifiedRef.current = true
    onSuccessRef.current?.()
  }, [])

  const [status, setStatus] = useState<ImportStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [allMessages, setAllMessages] = useState<string[]>([])
  const [allErrors, setAllErrors] = useState<string[]>([])
  const [taskId, setTaskId] = useState<string | null>(null)
  const [elapsedSec, setElapsedSec] = useState(0)
  const pollRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const logRef = useRef<HTMLDivElement>(null)
  const stoppedRef = useRef(false)
  const abortRef = useRef<AbortController | null>(null)

  const stopPolling = useCallback(() => {
    stoppedRef.current = true
    abortRef.current?.abort()
    abortRef.current = null
    if (pollRef.current) {
      clearTimeout(pollRef.current)
      pollRef.current = null
    }
  }, [])

  const handleClose = useCallback(() => {
    stopPolling()
    onClose()
  }, [onClose, stopPolling])

  useEffect(() => {
    return () => stopPolling()
  }, [stopPolling])

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
          Authorization: `Bearer ${token}`,
          Accept: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
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

  const applyStatus = useCallback((statusData: ImportStatus) => {
    setStatus(statusData)
    setAllMessages((prev) => {
      const newMessages = statusData.messages.filter((msg) => !prev.includes(msg))
      return [...prev, ...newMessages]
    })
    setAllErrors((prev) => {
      const newErrors = statusData.errors.filter((err) => !prev.includes(err))
      return [...prev, ...newErrors]
    })
  }, [])

  const handleImport = useCallback(async () => {
    setError(null)
    setStatus(null)
    stoppedRef.current = false

    try {
      const startData = await apiClient.post<{ task_id: string; log_id: number; status: string }>(
        '/api/v1/integrations/import',
        documentTypeRef.current === 'all' ? {} : { document_type: documentTypeRef.current },
      )

      if (!startData.task_id) {
        throw new Error('Не получен task_id от сервера')
      }

      setTaskId(startData.task_id)

      const first = await apiClient.get<ImportStatus>(
        `/api/v1/integrations/import/${startData.task_id}/status`,
      )
      applyStatus(first)

      const longPoll = async () => {
        if (!startData.task_id || stoppedRef.current) return

        try {
          abortRef.current?.abort()
          abortRef.current = new AbortController()
          const statusData = await apiClient.get<ImportStatus>(
            `/api/v1/integrations/import/${startData.task_id}/status/long`,
            abortRef.current.signal,
          )
          if (stoppedRef.current) return
          applyStatus(statusData)

          if (statusData.status === 'completed' || statusData.status === 'failed') {
            stopPolling()
            notifyList()
            return
          }

          void longPoll()
        } catch (e) {
          if (stoppedRef.current) return
          console.error('Ошибка Long Polling:', e)
          pollRef.current = setTimeout(() => {
            void longPoll()
          }, 2000)
        }
      }

      if (first.status === 'completed' || first.status === 'failed') {
        notifyList()
      } else {
        void longPoll()
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка импорта')
      stopPolling()
    }
  }, [applyStatus, stopPolling, notifyList])

  const startedRef = useRef(false)

  useEffect(() => {
    if (startedRef.current) return
    startedRef.current = true
    void handleImport()
  }, [handleImport])

  const isDone = status?.status === 'completed'
  const isFailed = status?.status === 'failed'
  const isBusy = !error && !isDone && !isFailed

  useEffect(() => {
    if (!isBusy) return
    const startedAt = Date.now()
    setElapsedSec(0)
    const id = window.setInterval(() => {
      setElapsedSec(Math.floor((Date.now() - startedAt) / 1000))
    }, 500)
    return () => window.clearInterval(id)
  }, [isBusy])

  const elapsedLabel = `${Math.floor(elapsedSec / 60)}:${String(elapsedSec % 60).padStart(2, '0')}`
  const headline =
    status?.current_step ||
    allMessages[allMessages.length - 1] ||
    'Запуск импорта…'

  return createPortal(
    <div
      className="dialog-backdrop"
      role="presentation"
      onClick={handleClose}
    >
      <div
        className="dialog dialog--wide dialog--import"
        role="dialog"
        aria-modal="true"
        aria-labelledby="import-title"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="dialog__head">
          <h3 id="import-title" className="dialog__title">
            {title}
          </h3>
          <button
            type="button"
            className="dialog__close"
            onClick={handleClose}
            data-close="true"
            aria-label="Закрыть"
            title="Закрыть"
          >
            ×
          </button>
        </div>

        {error ? (
          <p className="list-msg list-msg--err" role="alert">
            {error}
          </p>
        ) : null}

        <div className="import-progress">
          <div
            className={`import-progress__current-step${isBusy ? ' import-progress__current-step--busy' : ''}`}
          >
            {headline}
          </div>

          {status && status.total_rows > 0 ? (
            <div className="import-progress__bar">
              <div
                className="import-progress__fill"
                style={{
                  width: `${(status.processed_rows / status.total_rows) * 100}%`,
                }}
              />
            </div>
          ) : null}

          <div className="import-progress__stats">
            <div className="import-stat">
              <span className="import-stat__label">Всего</span>
              <span className="import-stat__value">{status?.total_rows ?? 0}</span>
            </div>
            <div className="import-stat">
              <span className="import-stat__label">Обработано</span>
              <span className="import-stat__value">{status?.processed_rows ?? 0}</span>
            </div>
            <div className="import-stat import-stat--success">
              <span className="import-stat__label">Успешно</span>
              <span className="import-stat__value">{status?.success_rows ?? 0}</span>
            </div>
            {(status?.error_rows ?? 0) > 0 ? (
              <div className="import-stat import-stat--error">
                <span className="import-stat__label">Ошибок</span>
                <span className="import-stat__value">{status?.error_rows}</span>
              </div>
            ) : null}
          </div>

          <div className="import-progress__log" ref={logRef}>
            {allMessages.length === 0 && allErrors.length === 0 ? (
              <div className="import-progress__log-line">Ожидаем воркер…</div>
            ) : null}
            {allMessages.map((msg, index) => (
              <div key={index} className="import-progress__log-line">
                {msg}
              </div>
            ))}
            {allErrors.map((err, index) => (
              <div
                key={`err-${index}`}
                className="import-progress__log-line import-progress__log-line--error"
              >
                ❌ {err}
              </div>
            ))}
          </div>
        </div>

        <div className="import-dialog-footer">
          {isBusy ? (
            <p className="import-progress__running">
              <span className="import-progress__spinner" aria-hidden />
              Импорт выполняется… {elapsedLabel}
            </p>
          ) : null}
          {isDone && !(status && status.error_rows > 0) ? (
            <p className="import-progress__done">✅ Импорт завершён</p>
          ) : null}
          {isFailed || (isDone && status && status.error_rows > 0) ? (
            <p className="import-progress__failed">Импорт завершён с замечаниями</p>
          ) : null}
          {error ? (
            <p className="import-progress__failed">Не удалось запустить импорт</p>
          ) : null}
          <div className="import-dialog-footer__buttons">
            {isFailed || (status && status.error_rows > 0) ? (
              <button
                type="button"
                className="import-dialog-btn import-dialog-btn--error"
                onClick={() => void downloadErrorsExcel()}
              >
                Скачать Excel с ошибками
              </button>
            ) : null}
            <button
              type="button"
              className="import-dialog-btn import-dialog-btn--primary"
              onClick={handleClose}
            >
              Закрыть
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body,
  )
}
