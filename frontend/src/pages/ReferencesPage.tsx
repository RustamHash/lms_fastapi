import { Link } from 'react-router-dom'

type ReferenceGroup = {
  title: string
  items: {
    to: string
    label: string
    description: string
  }[]
}

const REFERENCE_GROUPS: ReferenceGroup[] = [
  {
    title: 'Адреса',
    items: [
      { to: '/reference/addresses', label: 'Адреса', description: 'Канонические адреса' },
      { to: '/reference/address-input-aliases', label: 'Варианты ввода', description: 'Сырые адреса' },
      { to: '/reference/delivery-zones', label: 'Зоны доставки', description: 'Зоны на карте' },
    ],
  },
  {
    title: 'Контрагенты',
    items: [
      { to: '/reference/legal-entities', label: 'Юрлица', description: 'ИНН, КПП, ОГРН' },
      { to: '/reference/depositors', label: 'Поклажедатели', description: 'Владельцы груза' },
      { to: '/reference/clients', label: 'Клиенты', description: 'Клиенты поклажедателей' },
      { to: '/reference/trade-points', label: 'Торговые точки', description: 'Точки доставки' },
    ],
  },
  {
    title: 'Договоры и тарифы',
    items: [
      { to: '/reference/contracts', label: 'Договоры', description: 'Договоры с контрагентами' },
      { to: '/reference/tariffs', label: 'Тарифы', description: 'Услуги и цены' },
    ],
  },
  {
    title: 'Товары',
    items: [
      { to: '/reference/products', label: 'Товары', description: 'Номенклатура товаров' },
      { to: '/reference/batches', label: 'Партии', description: 'Партии товаров' },
      { to: '/reference/lpns', label: 'LPN', description: 'Паллеты' },
    ],
  },
  {
    title: 'Доставка',
    items: [
      { to: '/reference/drivers', label: 'Водители', description: 'Водители' },
      { to: '/reference/vehicles', label: 'Транспорт', description: 'Автомобили' },
      { to: '/reference/routes', label: 'Маршруты', description: 'Маршруты доставки' },
    ],
  },
]

export function ReferencesPage() {
  return (
    <section className="app-card app-card--wide">
      <h1 className="page-title">Справочники</h1>
      <p className="app-intro">Все справочники системы</p>

      <div className="ref-groups">
        {REFERENCE_GROUPS.map((group) => (
          <section key={group.title} className="ref-group">
            <h2 className="ref-group__title">{group.title}</h2>
            <div className="ref-group__cards">
              {group.items.map((item) => (
                <Link key={item.to} to={item.to} className="ref-card">
                  <span className="ref-card__title">{item.label}</span>
                  <span className="ref-card__desc">{item.description}</span>
                </Link>
              ))}
            </div>
          </section>
        ))}
      </div>
    </section>
  )
}
