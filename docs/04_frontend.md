# Фронтенд — структура

## Каталоги

frontend/src/
├── App.tsx # маршруты
├── main.tsx # точка входа
├── auth/
│ └── AuthContext.tsx # JWT, пользователь, permissions
├── components/
│ ├── DetailPageShell.tsx # обёртка detail-страниц, кнопка назад, хлебные крошки
│ ├── EntityListPage.tsx # универсальный список
│ ├── ListTableShell.tsx # таблица со сортировкой, фильтрами, колонками
│ ├── ListFilterCell.tsx # ячейка фильтра
│ ├── Layout.tsx # общий layout + notice strip
│ ├── Navbar.tsx # навигация
│ ├── RequireAuth.tsx # защита маршрутов
│ └── TableCellContextMenu.tsx # контекстное меню
├── features/
│ ├── entity-list/
│ │ ├── types.ts # ListPageConfig
│ │ ├── useEntityList.tsx # хук загрузки и фильтрации
│ │ ├── EntityListPage.tsx # рендер списка
│ │ └── columnUtils.ts # форматирование
│ ├── addresses/
│ │ ├── config.ts # конфиг списка адресов
│ │ └── addressInputAliasConfig.ts # конфиг алиасов
│ ├── legal-entities/
│ │ └── config.ts
│ ├── depositors/
│ │ └── config.ts
│ ├── clients/
│ │ └── config.ts
│ ├── trade-points/
│ │ └── config.ts
│ ├── contracts/
│ │ └── config.ts
│ └── tariffs/
│ └── config.ts
├── hooks/
│ ├── useColumnPrefs.ts # сохранение настроек колонок
│ └── useListController.ts # состояние списка
├── lib/
│ ├── http.ts # apiFetch с Bearer
│ └── token.ts # работа с sessionStorage
├── pages/
│ ├── ReferencesPage.tsx # страница справочников
│ ├── AddressesPage.tsx
│ ├── AddressDetailPage.tsx
│ ├── LegalEntitiesPage.tsx
│ ├── LegalEntityDetailPage.tsx
│ ├── LegalEntityCreatePage.tsx
│ ├── LegalEntityEditPage.tsx
│ └── ... другие страницы
└── styles/
 ├── app-layout.css
 └── list-pages.css

## Как работает список

1. Страница вызывает EntityListPage с config
2. useEntityList загружает данные через apiFetch
3. useColumnPrefs загружает/сохраняет настройки колонок
4. ListTableShell рендерит таблицу, фильтры, сортировку
5. Конфиг определяет: колонки, фильтры, URL, ссылки
