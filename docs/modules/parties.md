# parties — контрагенты и адреса

Справочник сторон 3PL: юрлица, роли (поклажедатель / хранитель / перевозчик), клиенты поклажедателя, адреса, зоны доставки, договоры и тарифы.

Код: `app/parties/`. HTTP: `app/api/v1/parties/`. DI-образец: `app/api/v1/parties/deps.py` (`get_*_service`).

---

## Зачем модуль

Заказы, остатки и доставка всегда «чьи-то». Поклажедатель — владелец товара. Клиент — грузополучатель/поставщик в контуре поклажедателя. Юрлицо одно, роли (depositor/keeper/carrier) — отдельные таблицы 1:1.

---

## Модели

| Класс | Таблица | Смысл |
|-------|---------|--------|
| `LegalEntity` | `parties_legal_entity` | ИНН/КПП, название, юр. данные |
| `Depositor` | `parties_depositor` | поклажедатель, `legal_entity_id` unique, `code` |
| `Keeper` | `parties_keeper` | хранитель (склад как юрлицо) |
| `Carrier` | `parties_carrier` | перевозчик |
| `Client` | `parties_client` | клиент поклажедателя: грузополучатель outbound (`client_id`) и поставщик inbound (`supplier_id`); unique `(depositor_id, code, delivery_address_id)` |
| `Address` | `parties_address` | нормализованный адрес |
| `RawAddress` | `parties_raw_address` | алиас ввода / сырая строка |
| `DeliveryZone` | `parties_delivery_zone` | зона доставки |
| `Contract` | `parties_contract` | договор |
| `TariffDocument`, `Tariff` | тарифные документы и ставки |

`ClientService.get_or_create` нужен импорту: нет клиента с кодом — создать, не падать.

---

## Сервисы

`AddressService`, `RawAddressService`, `LegalEntityService`, `DepositorService`, `ClientService`, `ContractService`, `TariffService`, `TariffDocumentService`, `DeliveryZoneService`, `CarrierService`, `KeeperService`.

Адреса: подсказки/нормализация через DaData (`app/infrastructure/external/dadata.py`), если заданы токены. Второй геокодер не подключать.

---

## API (`/api/v1`)

Типичный CRUD: `GET/POST ""`, `GET/PATCH/DELETE /{id}`.

| Префикс | Entity RBAC |
|---------|-------------|
| `/addresses` | `addresses` |
| `/aliases` | адреса (сырые/алиасы) |
| `/legal-entities` | `legal_entities` |
| `/depositors` | `depositors` |
| `/clients` | `clients` (список с `DataScope`) |
| `/contracts` | `contracts` |
| `/tariffs`, `/tariff-documents` | `tariffs` |
| `/delivery-zones` | `addresses` |
| `/carriers` | `carriers` |
| `/keepers` | `keepers` |

Список клиентов фильтруется скоупом пользователя.

---

## Связи

- **accounts** — `UserDepositor` / `UserClient`.
- **warehouse** — `Product.depositor_id`, `VirtualWarehouse.depositor_id`.
- **orders** — inbound/outbound/return несут `depositor_id`; outbound — `client_id`.
- **integration** — профиль привязан к поклажедателю. Создание заявки с обмена — `orders`, не integration.
- **delivery** — договор перевозки, адрес доставки.

---

## Состояние

Parties уже на фабриках `get_*_service` — образец для других доменов, не копировать `ServiceContainer`.
Скоуп только на клиентах. Поклажедатели и договоры не фильтруются.
Новые CRUD-справочники не добавлять, пока в `plans/STATUS.md` не закрыта задача `3`.
