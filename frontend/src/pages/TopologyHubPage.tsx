import { HubPage } from '../components/HubPage'

export function TopologyHubPage() {
  return (
    <HubPage
      title="Топология"
      subtitle="Структура склада"
      breadcrumbs={[{ label: 'Главная', to: '/' }, { label: 'Топология' }]}
      sections={[
        {
          title: 'Складская структура',
          icon: '🏗️',
          items: [
            { to: '/topology/warehouses', label: 'Склады', description: 'Физические склады', icon: '🏭' },
            { to: '/topology/virtual-warehouses', label: 'Виртуальные склады', description: 'Логические склады', icon: '🏢' },
            { to: '/topology/zones', label: 'Зоны', description: 'Зоны склада', icon: '🗂️' },
            { to: '/topology/rows', label: 'Ряды', description: 'Ряды стеллажей', icon: '📏' },
            { to: '/topology/locations', label: 'Ячейки', description: 'Места хранения', icon: '📦' },
          ],
        },
      ]}
    />
  )
}
