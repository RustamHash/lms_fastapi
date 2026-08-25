# files — файлы

Загрузка на диск и учёт в БД. Вертикальный срез: модели, схемы, роуты и сервис в `app/files/`, не в `app/api/v1/files/`. Подключён в `api_router` как `/api/v1/files`.

---

## Модель

`File` (таблица `files`): `file_path`, `file_type`, `original_name`, `size`, `mime_type`, `uploaded_by_id`.

Каталог на диске: `uploads/`. Расширения: pdf, jpg/png, doc(x), xls(x). Лимит 10 МБ. Путь проверяется, чтобы не выйти из `uploads`.

---

## API

| Метод | Путь | Право |
|-------|------|--------|
| POST | `/api/v1/files/upload` | `create` / `files` |
| GET | `/api/v1/files`, `/files/{id}` | `view` |
| GET | `/api/v1/files/{id}/download` | `view` |
| PATCH | `/api/v1/files/{id}` | `update` (тип файла) |
| DELETE | `/api/v1/files/{id}` | `delete` |

`FileService` + `FileRepository`. Локальный `get_service` в `routes.py`.

---

## Связи

`IntegrationLog` может ссылаться на файл. Фронт: `/files`, `/files-hub`. Не образец раскладки схем (`schemas.py` рядом с роутами).
