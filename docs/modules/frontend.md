# frontend — SPA

React 19 + Vite + React Router 7 + TanStack Query. Исходники: `frontend/src/`. CSS без фреймворка: переменные в `styles/variables.css`, модули в `styles/components/`.

Dev: Vite `:5173` (HMR). FastAPI `:8080` в `docker-compose.dev.yml` тоже отдаёт `frontend/dist` с хоста (том). После правок UI для `:8080` нужна сборка (`docker exec lms_dev_frontend npm run build`) и обновление страницы без кэша. Prod: тот же `frontend/dist`.

---

## Каркас

Провайдеры в `App.tsx`: `QueryClientProvider` → `AuthProvider` → `AppNoticeProvider` → `BrowserRouter`. Страницы — `React.lazy`.

| Путь | Роль |
|------|------|
| `auth/AuthContext.tsx` | login/logout, `/api/v1/auth/me`, хелперы прав |
| `lib/apiClient.ts` | `fetch` + Bearer, `ApiError`; GET с `cache: 'no-store'`; 401 → `/login` |
| `lib/token.ts` | `sessionStorage` ключ `sslogistics_access_token` |
| `hooks/usePermissions.ts` | `canView` / `canCreate` / … |
| `features/{entity}/config.ts` | `ListPageConfig`: `apiUrl`, `listPath`, колонки |
| `features/entity-system/` | `EntityListPage`; `useEntityList` держит строки, фильтры и сортировку; пресеты; `createForms.ts` — поля POST |
| `features/entity-fields/` | `GET /api/v1/entities/{key}/fields` |
| `components/GenericDetailPage.tsx` | простая карточка по id |
| `components/GenericCreatePage.tsx` | форма создания из `listPath` + `createForms` |
| `components/GenericDetailFromConfig.tsx` | деталка по колонкам config |
| `components/DetailPageShell.tsx` | оболочка кастомных деталок |
| `components/PlanFactTabs.tsx` | вкладки План / Факт / Расхождения (`list-table`). На факте: дата изготовления, срок годности, остаток срока (дн. и %) |
| `components/DetailDataTable.tsx` | таблица на классах списка |
| `pages/` | маршруты и хабы |

Хабы: `/`, `/references`, `/orders`, `/topology`, `/delivery`, `/documents-hub`, `/files-hub`, `/integrations`, `/system`, `/reports`.

В Navbar и `ReportsHubPage` есть ссылки `/reports/stock` и `/reports/movements` — маршрутов в `App.tsx` нет (отчёты — этап 8).

---

## Auth и права

Логин: `POST /api/v1/auth/token` (form, не `apiClient`) → токен → `GET /auth/me`. `hasPermission(user, module, action)` совпадает с каталогом бэкенда. Суперпользователь / `permissions.all` — полный доступ.

`RequireAuth` редиректит на `/login`. Скрытие меню и `canCreate` на списках — те же entity.

---

## Паттерн сущности

Большинство списков — `EntityListPage` + config (~40 `features/*/config.ts`).

1. Config: `entityKey`, `apiUrl`, **`listPath`** (SPA-путь списка). Деталка `{listPath}/{id}`, создание `{listPath}/new`.
2. Тонкая страница в `pages/`.
3. Маршрут в `App.tsx` / `entityCrudRoutes.tsx`.
4. Деталка: `GenericDetailPage` / `GenericDetailFromConfig`, `DetailPageShell` (users/roles/depositors/профили интеграций).
5. Ссылка в хабе / `Navbar.tsx` — `NavLink` / `Link` / `navigate()`, не `<a href>` внутри SPA.
6. Бэкенд: CRUD + запись в `MODEL_MAP` (`app/api/v1/meta.py`).

Клик по id и двойной клик по строке вызывают `navigate(listPath/id)`, не полную перезагрузку. «+» ведёт на `{listPath}/new` (если нет `toolbar.disableCreate`). Уже существующие формы (юрлица, поклажедатели, клиенты, договоры, зоны, склады, профили) остаются своими страницами. Адреса: карточка `/reference/addresses/:id` + редактирование `/edit` (зона доставки и поля адреса); на списке при выделении — компактная кнопка «Назначить зону» в тулбаре справа (рядом с иконками, без дубля «Выбрано»). Файлы — загрузка на `/files/new`. Логи интеграций не создаются вручную.

Маршрут `/new` регистрируется раньше `/:id`, иначе «new» попадает в param.

---

## Маршруты

Точный список — `App.tsx`. Группы:

| Зона | Пути |
|------|------|
| Заказы | `/orders/inbound\|outbound\|return` + `/new` + `/:id` |
| Справочники | `/reference/{addresses,depositors,clients,...}` + `/new` + `/:id` (группы, упаковки, товар-ячейка тоже) |
| Склад | `/stock`, `/tasks`, `/topology/{warehouses,virtual-warehouses,zones,rows,locations}` (+ `/new` и `/:id`) |
| Доставка | `/delivery/orders`, `/deviations`, `/route-lines` (+ `/new` и `/:id`) |
| Система | `/users`, `/roles`, `/audit`, `/notifications`, `/notification-rules` (+ `/new` и `/:id`) |
| Интеграции | `/integrations/profiles` (+ `/new`, `/:id`, `/:id/edit`), `/integrations/logs` + `/:id` |
| Файлы | `/files`, `/files/new`, `/files/:id` |

`features/stock/config.ts`: `lpn_id` обязателен (число, не `null`) — как в API add/remove/move. Деталка `StockDetailPage` те же поля. Новых экранов остатка, приёмки и отбора нет: воркфлоу — HTTP `/warehouse/receiving` и `/warehouse/picking`.

`features/inbound-orders/config.ts`: `number` — номер заявки (`DOC_NO`); `order_number` — номер заказа (пока может быть пустым, в PORDER нет); `loc_code` — код склада партнёра (`LOC`); `warehouse_name` — физический склад. Статусы на карточке и в списке — через `getStatusLabel` (`document_created` → «Документ создан»). Деталки `/orders/inbound/:id`, `/orders/outbound/:id`, `/documents/:id`: шапка + вкладки План / Факт / Расхождения (`components/PlanFactTabs.tsx`, таблица как на списках — `list-table` + `table-wrap`). API: `GET /warehouse/receiving/inbound/{id}`, `GET /warehouse/picking/outbound/{id}`, `GET /documents/{id}/plan-fact`.

Иконка «Импорт» на `/orders/inbound` и `/orders/outbound` (`ImportDialog`): сразу лента шагов, крестик и «Закрыть» (окно не обрезает футер); статус сначала `GET .../status`, потом `.../status/long`. Массовый прогон `POST /integrations/import` с типом `porder` / `order`. Это не выбор канала: канал — профиль на `/integrations/profiles`. Пошагово с исходящих: [outbound-import.md](../flows/outbound-import.md). Карточка профиля: пять FTP-папок, пароль, «Редактировать». После сохранения карточка показывает ответ PATCH, не закэшированный GET. Список логов `/integrations/logs` — `GET /api/v1/integrations/logs`. Кнопки «Забрать сейчас» на карточке ещё нет — см. [integration.md](integration.md).
