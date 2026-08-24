/**
 * Утилиты для работы с плоскими полями вложенных сущностей.
 */

export type FlatField = {
  /** Плоский путь: "legal_entity.name" */
  path: string
  /** Человекочитаемая метка */
  title: string
  /** Тип данных */
  type: 'text' | 'number' | 'date' | 'datetime' | 'bool'
}

const FIELD_LABELS: Record<string, string> = {
  id: 'ID',
  name: 'Название',
  code: 'Код',
  number: 'Номер',
  phone: 'Телефон',
  email: 'Email',
  inn: 'ИНН',
  kpp: 'КПП',
  ogrn: 'ОГРН',
  full_address: 'Полный адрес',
  region: 'Регион',
  city: 'Город',
  street: 'Улица',
  house: 'Дом',
  postal_code: 'Индекс',
  sku: 'Артикул',
  external_id: 'Внешний код',
  quantity: 'Количество',
  reserved_quantity: 'Зарезервировано',
  weight: 'Вес',
  volume: 'Объём',
  price: 'Цена',
  status: 'Статус',
  is_active: 'Активен',
  is_deleted: 'Удалён',
  is_edo: 'ЭДО',
  source_type: 'Тип источника',
  document_type: 'Тип документа',
  document_number: 'Номер документа',
  batch_number: 'Номер партии',
  production_date: 'Дата производства',
  expiration_date: 'Срок годности',
  legal_name: 'Полное наименование',
  contract_type: 'Тип договора',
  start_date: 'Дата начала',
  end_date: 'Дата окончания',
}

const MODEL_LABELS: Record<string, string> = {
  address: 'Адрес',
  legal_address: 'Юр. адрес',
  actual_address: 'Факт. адрес',
  delivery_address: 'Адрес доставки',
  delivery_zone: 'Зона доставки',
  outbound_order: 'Исходящий заказ',
  inbound_order: 'Входящий заказ',
  return_order: 'Возвратный заказ',
  legal_entity: 'Юрлицо',
  depositor: 'Поклажедатель',
  client: 'Клиент',
  product: 'Товар',
  warehouse: 'Склад',
  location: 'Ячейка',
  zone: 'Зона',
  batch: 'Партия',
  lpn: 'LPN',
  driver: 'Водитель',
  vehicle: 'Транспорт',
  route: 'Маршрут',
  carrier: 'Перевозчик',
  keeper: 'Хранитель',
  contract: 'Договор',
  tariff: 'Тариф',
}

function detectType(value: unknown): FlatField['type'] {
  if (value === null || value === undefined) return 'text'
  if (typeof value === 'boolean') return 'bool'
  if (typeof value === 'number') return 'number'
  if (typeof value === 'string') {
    if (/^\d{4}-\d{2}-\d{2}T/.test(value)) return 'datetime'
    if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return 'date'
    return 'text'
  }
  return 'text'
}

function makeLabel(path: string): string {
  const parts = path.split('.')
  const field = parts[parts.length - 1]
  const model = parts.length > 1 ? parts[parts.length - 2] : undefined

  const fieldLabel = FIELD_LABELS[field] ?? field
  if (model && MODEL_LABELS[model]) {
    return `${MODEL_LABELS[model]} — ${fieldLabel}`
  }
  return fieldLabel
}

/** Рекурсивно разворачивает вложенный объект в плоские поля (до 5 уровней) */
export function flattenFields(
  obj: Record<string, unknown>,
  prefix = '',
  depth = 0,
  maxDepth = 5,
): FlatField[] {
  const result: FlatField[] = []

  for (const [key, value] of Object.entries(obj)) {
    const fullPath = prefix ? `${prefix}.${key}` : key

    if (value === null || typeof value !== 'object' || Array.isArray(value)) {
      // Простое значение
      result.push({
        path: fullPath,
        title: makeLabel(fullPath),
        type: detectType(value),
      })
      continue
    }

    const meta = value as Record<string, unknown>

    // Если это метаданные поля (есть title и type)
    if ('title' in meta && 'type' in meta) {
      const fieldType = String(meta.type)

      // Если type === 'object' и есть nested — рекурсивно обрабатываем nested
      if (fieldType === 'object' && meta.nested && typeof meta.nested === 'object') {
        const nested = flattenFields(
          meta.nested as Record<string, unknown>,
          fullPath,
          depth + 1,
          maxDepth,
        )
        result.push(...nested)
      } else if (depth >= maxDepth) {
        // Достигнут предел глубины — добавить как поле
        result.push({
          path: fullPath,
          title: String(meta.title ?? makeLabel(fullPath)),
          type: detectType(meta.default ?? meta.type),
        })
      } else {
        // Обычное поле
        result.push({
          path: fullPath,
          title: String(meta.title ?? makeLabel(fullPath)),
          type: detectType(meta.default ?? meta.type),
        })
      }
    } else if (depth < maxDepth) {
      // Вложенный объект без метаданных — рекурсивно обрабатываем
      const nested = flattenFields(
        meta,
        fullPath,
        depth + 1,
        maxDepth,
      )
      result.push(...nested)
    }
  }

  return result
}

/** Получить значение по плоскому пути */
export function getNestedValue(
  obj: Record<string, unknown> | null | undefined,
  path: string,
): unknown {
  if (obj == null) return null
  if (!path.includes('.')) return obj[path] ?? null

  return path.split('.').reduce<unknown>((acc, key) => {
    if (acc == null || typeof acc !== 'object') return null
    return (acc as Record<string, unknown>)[key] ?? null
  }, obj)
}

/** Поля по умолчанию — без системных */
export function getDefaultFields(
  flatFields: FlatField[] | Record<string, unknown>,
  maxFields = 8,
): FlatField[] {
  const fields = Array.isArray(flatFields)
    ? flatFields
    : flattenFields(flatFields as Record<string, unknown>)

  const systemPatterns = [
    /^id$/,
    /\.id$/,
    /_id$/,
    /_at$/,
    /_by$/,
    /^is_deleted$/,
    /\.is_deleted$/,
    /^deleted_at$/,
  ]

  const filtered = fields.filter((f) => {
    return !systemPatterns.some((p) => p.test(f.path))
  })

  return filtered.slice(0, maxFields)
}

/** Отображаемые поля — не системные */
export function getDisplayableFields(
  flatFields: FlatField[] | Record<string, unknown>,
): FlatField[] {
  const fields = Array.isArray(flatFields)
    ? flatFields
    : flattenFields(flatFields as Record<string, unknown>)

  const systemPatterns = [
    /^id$/,
    /\.id$/,
    /_id$/,
    /_at$/,
    /_by$/,
    /^is_deleted$/,
    /\.is_deleted$/,
    /^deleted_at$/,
  ]

  return fields.filter((f) => {
    return !systemPatterns.some((p) => p.test(f.path))
  })
}
