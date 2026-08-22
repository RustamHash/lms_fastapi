import { HubPage } from '../components/HubPage'

export function ReferencesPage() {
  return (
    <HubPage
      title="Справочники"
      subtitle="Все справочники системы"
      breadcrumbs={[{ label: 'Главная', to: '/' }, { label: 'Справочники' }]}
      sections={[
        {
          title: 'Адреса',
          icon: '📍',
          items: [
            { to: '/reference/addresses', label: 'Адреса', description: 'Канонические адреса', icon: '🏠' },
            { to: '/reference/address-input-aliases', label: 'Варианты ввода', description: 'Сырые адреса', icon: '✏️' },
            { to: '/reference/delivery-zones', label: 'Зоны доставки', description: 'Зоны на карте', icon: '🗺️' },
          ],
        },
        {
          title: 'Контрагенты',
          icon: '👥',
          items: [
            { to: '/reference/legal-entities', label: 'Юрлица', description: 'ИНН, КПП, ОГРН', icon: '🏢' },
            { to: '/reference/depositors', label: 'Поклажедатели', description: 'Владельцы груза', icon: '📦' },
            { to: '/reference/clients', label: 'Клиенты', description: 'Клиенты поклажедателей', icon: '🤝' },
            { to: '/carriers', label: 'Перевозчики', description: 'Транспортные компании', icon: '🚛' },
            { to: '/keepers', label: 'Хранители', description: 'Ответственное хранение', icon: '🏬' },
          ],
        },
        {
          title: 'Договоры и тарифы',
          icon: '📄',
          items: [
            { to: '/reference/contracts', label: 'Договоры', description: 'Договоры с контрагентами', icon: '📝' },
            { to: '/reference/tariffs', label: 'Тарифы', description: 'Услуги и цены', icon: '💰' },
            { to: '/reference/tariff-documents', label: 'Документы тарифов', description: 'Утверждённые тарифы', icon: '📋' },
          ],
        },
        {
          title: 'Товары',
          icon: '📦',
          items: [
            { to: '/reference/products', label: 'Товары', description: 'Номенклатура товаров', icon: '🏷️' },
            { to: '/reference/product-groups', label: 'Группы товаров', description: 'Категории товаров', icon: '📂' },
            { to: '/reference/packages', label: 'Упаковки', description: 'Виды упаковок', icon: '📦' },
            { to: '/reference/batches', label: 'Партии', description: 'Партии товаров', icon: '🔢' },
            { to: '/reference/lpns', label: 'LPN', description: 'Паллеты и упаковки', icon: '📦' },
          ],
        },
        {
          title: 'Топология',
          icon: '🏗️',
          items: [
            { to: '/topology/warehouses', label: 'Склады', description: 'Физические склады', icon: '🏭' },
            { to: '/topology/virtual-warehouses', label: 'Виртуальные склады', description: 'Логические склады', icon: '🏢' },
            { to: '/topology/zones', label: 'Зоны', description: 'Зоны склада', icon: '🗂️' },
            { to: '/topology/rows', label: 'Ряды', description: 'Ряды стеллажей', icon: '📏' },
            { to: '/topology/locations', label: 'Ячейки', description: 'Места хранения', icon: '📦' },
            { to: '/reference/product-locations', label: 'Товар-ячейка', description: 'Привязка товаров', icon: '🔗' },
          ],
        },
        {
          title: 'Доставка',
          icon: '🚚',
          items: [
            { to: '/reference/drivers', label: 'Водители', description: 'Водители', icon: '👤' },
            { to: '/reference/vehicles', label: 'Транспорт', description: 'Автомобили', icon: '🚗' },
            { to: '/reference/routes', label: 'Маршруты', description: 'Маршруты доставки', icon: '🗺️' },
          ],
        },
      ]}
    />
  )
}
