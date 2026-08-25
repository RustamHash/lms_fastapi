# notifications — уведомления

In-app и email по правилам, подписанным на `event_bus`. Не путать с UI-тостами (`frontend` `AppNoticeContext`).

Код: `app/notifications/`. HTTP: `app/api/v1/notifications/`.

---

## Модели

**Notification** (`notifications_notification`): получатель `user_id`, заголовок/текст, `notification_type`, `status` (`pending` и далее), `link`, `sent_at` / `read_at`.

**NotificationRule**: событие, канал (`app` / `email`), получатель (конкретный user или роль по `role_code`), активность.

---

## Поток

1. Сервис фичи делает `event_bus.emit(EventTypes.…, data)`.
2. На старте `setup_notification_dispatcher` подписывает `NotificationDispatcher.handle_event`.
3. Диспетчер открывает **свою** сессию (не сессию HTTP-запроса), читает активные правила, шлёт через `AppAdapter` или `EmailAdapter`.

Обработчик не должен рассчитывать на UoW исходного запроса.

Адаптеры: `app/notifications/adapters/`.

---

## API

| Путь | Назначение |
|------|------------|
| `/api/v1/notifications` | список/прочтение своих уведомлений |
| `/api/v1/notification-rules` | CRUD правил |

RBAC: `notifications`.

---

## Связи

Типы событий задаёт `app/infrastructure/events/event_types.py` (импорт, документ, доставка, задание). Новый emit — добавить константу, правило в UI, строку в этой доке и в [infrastructure.md](infrastructure.md).
