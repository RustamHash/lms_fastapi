import { Outlet } from 'react-router-dom'
import { useAppNotice } from '../notifications/AppNoticeContext'
import { Navbar } from './Navbar'

export function Layout() {
  const { notice } = useAppNotice()
  const icon = notice?.kind === 'success' ? '✓' : notice?.kind === 'error' ? '⚠' : 'ℹ'

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
