import { Link } from 'react-router-dom'

const ORDER_CARDS = [
  {
    to: '/orders/inbound',
    label: 'Входящие заказы',
    description: 'Заказы от поставщиков',
  },
  {
    to: '/orders/outbound',
    label: 'Исходящие заказы',
    description: 'Заказы клиентов',
  },
  {
    to: '/orders/return',
    label: 'Возвратные заказы',
    description: 'Возвраты от клиентов',
  },
]

export function OrdersHubPage() {
  return (
    <section className="app-card app-card--wide">
      <h1 className="page-title">Заказы</h1>
      <p className="app-intro">Управление заказами</p>

      <div className="ref-groups">
        <section className="ref-group">
          <h2 className="ref-group__title">Типы заказов</h2>
          <div className="ref-group__cards">
            {ORDER_CARDS.map((item) => (
              <Link key={item.to} to={item.to} className="ref-card">
                <span className="ref-card__title">{item.label}</span>
                <span className="ref-card__desc">{item.description}</span>
              </Link>
            ))}
          </div>
        </section>
      </div>
    </section>
  )
}
