import { useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import { useAppNotice } from '../notifications/AppNoticeContext'
import { Navbar } from './Navbar'

export function Layout() {
  const { notice } = useAppNotice()
  const icon = notice?.kind === 'success' ? '✓' : notice?.kind === 'error' ? '⚠' : 'ℹ'

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // Esc — закрыть модальное окно
      if (e.key === 'Escape') {
        const dialog = document.querySelector('.dialog-backdrop, .quick-nav-backdrop')
        if (dialog) {
          // Находим кнопку "Отмена" или "Закрыть"
          const cancelBtn = dialog.querySelector('.tb--reset, [data-close="true"]')
          if (cancelBtn && cancelBtn instanceof HTMLElement) {
            cancelBtn.click()
          }
        }
      }
      
      // Ctrl+Enter — сохранить форму
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const form = document.querySelector('form')
        if (form) {
          const submitBtn = form.querySelector('button[type="submit"]')
          if (submitBtn && submitBtn instanceof HTMLElement && !submitBtn.hasAttribute('disabled')) {
            e.preventDefault()
            submitBtn.click()
          }
        }
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  return (
    <>
      <Navbar />
      <div className="app-notice-strip" role="status" aria-live="polite">
        {notice ? (
          <p className={`app-notice-strip__text app-notice-strip__text--${notice.kind}`}>
            <span className="app-notice-strip__icon" aria-hidden>
              {icon}
            </span>
            <span>{notice.message}</span>
          </p>
        ) : (
          <p className="app-notice-strip__text app-notice-strip__text--idle">
            <span className="app-notice-strip__icon" aria-hidden>
              ℹ
            </span>
            <span>—</span>
          </p>
        )}
      </div>
      <main id="main-content" className="app-main">
        <Outlet />
      </main>
    </>
  )
}
