import { HubPage } from '../components/HubPage'

export function ReportsHubPage() {
  return (
    <HubPage
      title="Отчёты"
      subtitle="Формирование отчётов"
      breadcrumbs={[{ label: 'Главная', to: '/' }, { label: 'Отчёты' }]}
      sections={[
        {
          title: 'Складские отчёты',
          icon: '📊',
          items: [
            { to: '/reports/stock', label: 'Остатки', description: 'Остатки на складе', icon: '📦' },
            { to: '/reports/movements', label: 'Движения', description: 'Движения товаров', icon: '🔄' },
          ],
        },
        {
          title: 'Будущие отчёты',
          icon: '🔮',
          items: [
            { to: '/reports', label: 'Заказы', description: 'Отчёт по заказам (скоро)', icon: '📋', badge: 'Скоро' },
            { to: '/reports', label: 'Доставка', description: 'Отчёт по доставке (скоро)', icon: '🚚', badge: 'Скоро' },
          ],
        },
      ]}
    />
  )
}
