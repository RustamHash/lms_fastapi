# Изменения доступа и портала (аудит F0–F10)

## Модель доступа

- **Оператор склада** (`User.is_portal_user=False`): видит всех поклажедателей; режут только роли/права.
- **Пользователь портала** (`is_portal_user=True`): только `/api/v1/portal/*` и `/api/v1/auth/*` (клетка `PortalCageMiddleware` + JWT claim `portal`); данные только своих `UserDepositor`.
- Без привязки у портального пользователя — отказ при логине, не «открой всё».

## Платформа

- Audit: отдельная сессия + `commit` после успешного mutating-запроса.
- Soft-delete по умолчанию в `BaseRepository`.
- Rate-limit auth через Redis (fallback in-memory).
- Outbound→delivery: retry handler + Celery `ensure_delivery_for_outbound`.
- Маршрут: `POST /delivery/routes/{id}/assign` → `ROUTE_ASSIGNED`.
- DeliveryOrder: опциональный `tariff_id`.

## Портал

- API: `/api/v1/portal` (me, dashboard, products, orders, stock).
- UI: `/portal` (отдельный shell), операторский SPA закрыт через `RequireOperator`.
