import type { CreateField, ListPageConfig } from './types'

const CREATE_FORMS: Record<string, { fields: CreateField[]; apiUrl?: string }> = {
  products: {
    fields: [
      { key: 'depositor_id', label: 'Поклажедатель ID', type: 'number', required: true },
      { key: 'external_id', label: 'Внешний код', type: 'text', required: true },
      { key: 'name', label: 'Наименование', type: 'text', required: true },
      { key: 'sku', label: 'Артикул', type: 'text' },
      { key: 'legal_name', label: 'Полное наименование', type: 'text' },
      { key: 'weight', label: 'Вес нетто', type: 'text' },
      { key: 'volume', label: 'Объём', type: 'text' },
    ],
  },
  product_groups: {
    fields: [{ key: 'name', label: 'Название', type: 'text', required: true }],
  },
  packages: {
    fields: [
      { key: 'product_id', label: 'Товар ID', type: 'number', required: true },
      { key: 'name', label: 'Название', type: 'text', required: true },
      { key: 'quantity', label: 'Количество в упаковке', type: 'number' },
      { key: 'barcode', label: 'Штрихкод', type: 'text' },
    ],
  },
  product_locations: {
    fields: [
      { key: 'product_id', label: 'Товар ID', type: 'number', required: true },
      { key: 'location_id', label: 'Ячейка ID', type: 'number', required: true },
    ],
  },
  batches: {
    fields: [
      { key: 'product_id', label: 'Товар ID', type: 'number', required: true },
      { key: 'batch_number', label: 'Номер партии', type: 'text' },
      { key: 'production_date', label: 'Дата производства', type: 'date' },
      { key: 'expiration_date', label: 'Срок годности', type: 'date' },
    ],
  },
  lpns: {
    fields: [{ key: 'status', label: 'Статус', type: 'text' }],
  },
  addresses: {
    fields: [
      { key: 'full_address', label: 'Полный адрес', type: 'text', required: true },
      { key: 'city', label: 'Город', type: 'text' },
      { key: 'street', label: 'Улица', type: 'text' },
      { key: 'house', label: 'Дом', type: 'text' },
      { key: 'postal_code', label: 'Индекс', type: 'text' },
    ],
  },
  address_input_aliases: {
    fields: [
      { key: 'raw_text', label: 'Сырой адрес', type: 'textarea', required: true },
      { key: 'source', label: 'Источник', type: 'text' },
    ],
  },
  tariffs: {
    fields: [
      { key: 'document_id', label: 'Тарифный документ ID', type: 'number', required: true },
      { key: 'service_group', label: 'Группа услуг', type: 'text', required: true },
      { key: 'name', label: 'Название', type: 'text', required: true },
      { key: 'unit', label: 'Единица', type: 'text', required: true },
      { key: 'price', label: 'Цена', type: 'text', required: true },
      { key: 'description', label: 'Описание', type: 'textarea' },
    ],
  },
  tariff_documents: {
    fields: [
      { key: 'contract_id', label: 'Договор ID', type: 'number', required: true },
      { key: 'document_type', label: 'Тип документа', type: 'text', required: true },
      { key: 'number', label: 'Номер', type: 'text', required: true },
      { key: 'document_date', label: 'Дата подписания', type: 'date', required: true },
      { key: 'valid_from', label: 'Действует с', type: 'date', required: true },
      { key: 'valid_until', label: 'Действует до', type: 'date' },
      { key: 'currency', label: 'Валюта', type: 'text' },
    ],
  },
  drivers: {
    fields: [
      { key: 'name', label: 'ФИО', type: 'text', required: true },
      { key: 'phone', label: 'Телефон', type: 'text' },
      { key: 'carrier_id', label: 'Перевозчик ID', type: 'number' },
    ],
  },
  vehicles: {
    fields: [
      { key: 'number', label: 'Гос. номер', type: 'text', required: true },
      { key: 'brand', label: 'Марка', type: 'text' },
      { key: 'model', label: 'Модель', type: 'text' },
      { key: 'capacity', label: 'Грузоподъёмность', type: 'number' },
      { key: 'volume', label: 'Объём', type: 'number' },
      { key: 'carrier_id', label: 'Перевозчик ID', type: 'number' },
    ],
  },
  routes: {
    fields: [
      { key: 'number', label: 'Номер', type: 'text', required: true },
      { key: 'driver_id', label: 'Водитель ID', type: 'number', required: true },
      { key: 'vehicle_id', label: 'Автомобиль ID', type: 'number', required: true },
      { key: 'route_date', label: 'Дата', type: 'date', required: true },
    ],
  },
  carriers: {
    fields: [{ key: 'legal_entity_id', label: 'Юрлицо ID', type: 'number', required: true }],
  },
  keepers: {
    fields: [{ key: 'legal_entity_id', label: 'Юрлицо ID', type: 'number', required: true }],
  },
  topology_zones: {
    fields: [
      { key: 'warehouse_id', label: 'Склад ID', type: 'number', required: true },
      { key: 'name', label: 'Название', type: 'text', required: true },
      { key: 'zone_type', label: 'Тип зоны', type: 'text', required: true },
    ],
  },
  topology_rows: {
    fields: [
      { key: 'zone_id', label: 'Зона ID', type: 'number', required: true },
      { key: 'code', label: 'Код ряда', type: 'text', required: true },
      { key: 'row_type', label: 'Тип ряда', type: 'text', required: true },
    ],
  },
  topology_locations: {
    fields: [
      { key: 'row_id', label: 'Ряд ID', type: 'number', required: true },
      { key: 'position', label: 'Позиция', type: 'number', required: true },
      { key: 'level', label: 'Ярус', type: 'number' },
    ],
  },
  inbound_orders: {
    fields: [
      { key: 'depositor_id', label: 'Поклажедатель ID', type: 'number', required: true },
      { key: 'warehouse_id', label: 'Склад ID', type: 'number' },
      { key: 'number', label: 'Номер заявки', type: 'text', required: true },
      { key: 'loc_code', label: 'Код склада (LOC)', type: 'text', required: true },
      { key: 'supplier_id', label: 'Поставщик ID', type: 'number', required: true },
      { key: 'order_date', label: 'Дата заявки', type: 'date', required: true },
      { key: 'notes', label: 'Примечания', type: 'textarea' },
    ],
  },
  outbound_orders: {
    apiUrl: '/api/v1/outbound-orders',
    fields: [
      { key: 'depositor_id', label: 'Поклажедатель ID', type: 'number', required: true },
      { key: 'warehouse_id', label: 'Склад ID', type: 'number' },
      { key: 'number', label: 'Номер заявки', type: 'text', required: true },
      { key: 'client_id', label: 'Клиент ID', type: 'number', required: true },
      { key: 'order_date', label: 'Дата заявки', type: 'date', required: true },
      { key: 'delivery_address_name', label: 'Адрес доставки', type: 'text' },
      { key: 'notes', label: 'Примечания', type: 'textarea' },
    ],
  },
  return_orders: {
    fields: [
      { key: 'outbound_order_id', label: 'Исходящий заказ ID', type: 'number', required: true },
      { key: 'depositor_id', label: 'Поклажедатель ID', type: 'number', required: true },
      { key: 'warehouse_id', label: 'Склад ID', type: 'number' },
      { key: 'return_date', label: 'Дата возврата', type: 'date', required: true },
      { key: 'return_type', label: 'Тип возврата', type: 'text' },
      { key: 'notes', label: 'Примечания', type: 'textarea' },
    ],
  },
  'delivery-orders': {
    fields: [
      { key: 'number', label: 'Номер', type: 'text', required: true },
      { key: 'contract_id', label: 'Договор ID', type: 'number' },
      { key: 'document_id', label: 'Документ ID', type: 'number' },
      { key: 'outbound_order_id', label: 'Исходящий заказ ID', type: 'number' },
      { key: 'contact_person', label: 'Контакт', type: 'text' },
      { key: 'phone', label: 'Телефон', type: 'text' },
      { key: 'delivery_date', label: 'Дата доставки', type: 'date' },
      { key: 'comment', label: 'Комментарий', type: 'textarea' },
    ],
  },
  deviations: {
    fields: [
      { key: 'delivery_order_id', label: 'Заказ доставки ID', type: 'number', required: true },
      { key: 'deviation_type', label: 'Тип', type: 'text', required: true },
      { key: 'quantity', label: 'Количество', type: 'number' },
      { key: 'description', label: 'Описание', type: 'textarea' },
    ],
  },
  route_lines: {
    fields: [
      { key: 'route_id', label: 'Маршрут ID', type: 'number', required: true },
      { key: 'delivery_order_id', label: 'Заказ доставки ID', type: 'number', required: true },
      { key: 'order', label: 'Порядок', type: 'number' },
      { key: 'status', label: 'Статус', type: 'text' },
    ],
  },
  documents: {
    fields: [
      { key: 'document_type', label: 'Тип документа', type: 'text', required: true },
      { key: 'warehouse_id', label: 'Склад ID', type: 'number', required: true },
      { key: 'document_number', label: 'Номер', type: 'text', required: true },
      { key: 'document_date', label: 'Дата', type: 'date' },
      { key: 'contract_id', label: 'Договор ID', type: 'number' },
    ],
  },
  users: {
    fields: [
      { key: 'username', label: 'Имя пользователя', type: 'text', required: true },
      { key: 'password', label: 'Пароль', type: 'password', required: true },
      { key: 'phone', label: 'Телефон', type: 'text' },
      { key: 'email', label: 'Email', type: 'text' },
    ],
  },
  roles: {
    fields: [
      { key: 'name', label: 'Название', type: 'text', required: true },
      { key: 'code', label: 'Код', type: 'text', required: true },
    ],
  },
  notifications: {
    fields: [
      { key: 'user_id', label: 'Получатель ID', type: 'number', required: true },
      { key: 'title', label: 'Заголовок', type: 'text', required: true },
      { key: 'text', label: 'Текст', type: 'textarea', required: true },
      { key: 'notification_type', label: 'Тип', type: 'text' },
      { key: 'link', label: 'Ссылка', type: 'text' },
    ],
  },
  notification_rules: {
    fields: [
      { key: 'event_type', label: 'Событие', type: 'text', required: true },
      { key: 'channel', label: 'Канал (app/email)', type: 'text', required: true },
      { key: 'recipient_type', label: 'Тип получателя (user/role)', type: 'text', required: true },
      { key: 'recipient_id', label: 'Получатель ID', type: 'number' },
      { key: 'role_code', label: 'Код роли', type: 'text' },
    ],
  },
  audit: {
    fields: [
      { key: 'action', label: 'Действие', type: 'text', required: true },
      { key: 'entity_type', label: 'Тип объекта', type: 'text', required: true },
      { key: 'entity_id', label: 'ID объекта', type: 'text' },
    ],
  },
  tasks: {
    fields: [
      { key: 'task_type', label: 'Тип задания', type: 'text', required: true },
      { key: 'document_id', label: 'Документ ID', type: 'number' },
      { key: 'assignee_id', label: 'Исполнитель ID', type: 'number' },
    ],
  },
  stock: {
    apiUrl: '/api/v1/warehouse/stock/add',
    fields: [
      { key: 'product_id', label: 'Товар ID', type: 'number', required: true },
      { key: 'location_id', label: 'Ячейка ID', type: 'number', required: true },
      { key: 'lpn_id', label: 'LPN ID', type: 'number', required: true },
      { key: 'batch_id', label: 'Партия ID', type: 'number', required: true },
      { key: 'quantity', label: 'Количество', type: 'text', required: true },
    ],
  },
}

export function resolveCreateForm<Row extends { id: number }>(config: ListPageConfig<Row>): {
  fields: CreateField[]
  apiUrl: string
} | null {
  const preset = CREATE_FORMS[config.entityKey]
  const fields = config.createFields ?? preset?.fields
  if (!fields || fields.length === 0) return null
  return {
    fields,
    apiUrl: config.createApiUrl ?? preset?.apiUrl ?? config.apiUrl,
  }
}

export function listCreatePath<Row extends { id: number }>(config: ListPageConfig<Row>): string | undefined {
  if (config.toolbar?.disableCreate) return undefined
  if (config.toolbar?.createHref) return config.toolbar.createHref
  if (config.listPath) return `${config.listPath}/new`
  return undefined
}

export function listDetailPath<Row extends { id: number }>(
  config: ListPageConfig<Row>,
  row: Row,
): string | undefined {
  const selfHref = config.columnOverrides?.id?.href
  if (selfHref) return selfHref(row)
  if (config.listPath) return `${config.listPath}/${row.id}`
  return undefined
}
