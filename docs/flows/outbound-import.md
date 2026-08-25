# Импорт с `/orders/outbound`

Пошаговый путь: иконка «Импорт» на списке исходящих → диалог → `POST /import` → Celery → FTP.

Экран: FastAPI `:8080` отдаёт SPA; запросы идут на `/api/v1/...`. То же окно с входящих (`porder`), здесь тип документа другой.

Код: `frontend/src/pages/OutboundOrdersPage.tsx`, `frontend/src/components/ImportDialog.tsx`, `frontend/src/components/table/TableToolbar.tsx`, `app/api/v1/integration/routes_import.py`, `app/tasks.py`, `app/integration/services/import_run_service.py`, `app/integration/adapters/zln_adapter.py`.

**С этой страницы исходящие заявки с обмена не создаются.** Кнопка запускает тот же конвейер, что у входящих, с фильтром файлов `order_*`. XML с корнем `ORDER` адаптер отклоняет.

---

## 1. Страница

1. Маршрут `/orders/outbound` → `OutboundOrdersPage` (нужна авторизация).
2. Список — `EntityListPage` + `outboundOrdersConfig` (загрузка исходящих с API). К импорту не относится.
3. В тулбар передаётся `onImport={() => setImportOpen(true)}`.
4. В `TableToolbar` кнопка с `aria-label="Импорт"` (иконка). Подтверждения нет.

## 2. Открытие диалога

5. `importOpen = true` → монтируется `ImportDialog`:
   - `documentType="order"`
   - `title="Импорт расходных заказов"`
   - `onClose` сбрасывает флаг.
6. Диалог через портал в `document.body`: затемнение + окно.
7. Сразу после монтирования `useEffect` один раз вызывает `handleImport` (`startedRef`). Повторного клика в этом окне нет — импорт стартует сам.

Сразу видны заголовок, лента («Ожидаем воркер…»), счётчики, крестик и «Закрыть». Пока воркер молчит, секунды в футере тикают — окно не зависло.

## 3. `POST /api/v1/integrations/import`

8. Тело: `{ "document_type": "order" }`.
9. Заголовок `Authorization: Bearer` из sessionStorage. Без токена — 401 и переход на `/login`.
10. Право: `create` на сущность `integrations`. Иначе 403. Права списка заказов для этой кнопки не проверяются.

Сервер (`start_import` в `routes_import.py`):

11. Открывается UoW (сессия HTTP-запроса).
12. `task_id` = новый UUID.
13. Строка `integration_log`: `status="starting"`, `document_type="order"`, `created_by_id` пользователя.
14. В Redis/Celery ставится задача `app.tasks.run_import`, аргументы `[task_id, user_id, "order"]`, очередь `imports`.
15. Ответ 200, **не дожидаясь FTP**:
    `{ task_id, celery_task_id, status: "queued" }`.
16. Коммит UoW — лог уже в БД, фронт может опрашивать статус.

HTTP на этом закончил. Дальше работает воркер.

## 4. Фронт после POST

17. Сохраняется `taskId`.
18. Сразу `GET .../status` (не long) — окно заполняется без ожидания 25 с.
19. Пока статус не финальный: `GET .../status/long` ждёт смену лога или ~25 с, затем снова.
20. Новые `messages` / `errors` дописываются в ленту. `current_step` — крупная строка сверху.
21. «Закрыть» (и клик по фону) всегда есть: останавливает опрос и закрывает окно. Celery при этом не убивается.

## 5. Что видно в диалоге

Сразу: заголовок, «Запуск импорта…» / «Ожидаем воркер…», счётчики 0, «выполняется…», **Закрыть**.

Дальше в ленте — шаги воркера: задача принята, сколько профилей, FTP, каталог, файл, ошибки (пустой FTP, нет `in_path`, ORDER не принимается и т.д.).

| Элемент | Когда |
|--------|--------|
| Крупная строка | `current_step` или последнее сообщение |
| Полоса прогресса | `total_rows > 0` |
| Счётчики | всегда |
| Лента | `messages` и `errors` |
| Excel | были ошибки строк |
| Закрыть | всегда |

## 6. Начало работы воркера

22. `celery_worker` берёт задачу; свой движок Postgres без пула (`create_worker_engine`).
23. `ImportRunService.run` пишет шаги в `integration_log.messages` (и ошибки в `errors`) отдельными коммитами, чтобы окно их видело.
24. `_prepare`: активные профили; без FTP/`in_path`/хоста — строка в лог, профиль пропускается.
25. По профилю: «подключаемся к FTP» → список `in_path` → файлы `order_*`.
26. Нет таких файлов — сообщение в ленте, не обязательно `failed` всего прогона.
27. Файл → `ZLNAdapter.parse`. `ORDER` → в ленте «исходящий ORDER пока не принимается». `accept` не вызывается.
28. Сбой воркера пишется в лог как `failed`, чтобы окно не крутилось вечно.

---

## Итог

С исходящих это массовый прогон всех FTP-профилей с фильтром `order_*`. Диалог показывает журнал `integration_log`. Создание расходных заказов из XML — ещё не сделано.

Входящие (`/orders/inbound`) отличаются только `documentType="porder"` и заголовком диалога. Там PORDER принимается в `orders`.
