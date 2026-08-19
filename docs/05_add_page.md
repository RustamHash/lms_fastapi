# Как добавить новую страницу

## Шаг 1: Конфиг

Создать frontend/src/features/{entity}/config.ts:

typescript
import type { ListPageConfig } from '../entity-list/types'

type EntityRow = {
 id: number
 name: string
 // поля из API
}

export const entityConfig = {
 list: {
 entityKey: 'entities',
 title: 'Название',
 apiUrl: '/api/v1/...',
 columns: [
 { id: 'id', label: 'ID', type: 'number' },
 { id: 'name', label: 'Название', type: 'text' },
 ],
 filters: [
 { id: 'name', type: 'text', label: 'Название' },
 ],
 toolbar: {
 createHref: '/reference/entities/new',
 },
 columnOverrides: {
 name: { href: (row) => `/reference/entities/${row.id}` },
 },
 } as ListPageConfig<EntityRow>,
}


## Шаг 2: Страница списка

Создать frontend/src/pages/EntitiesPage.tsx:
typescript
import { useNavigate } from 'react-router-dom'
import { EntityListPage } from '../features/entity-list/EntityListPage'
import { entityConfig } from '../features/entities/config'

export function EntitiesPage() {
 const navigate = useNavigate()
 return (
 <EntityListPage
 config={entityConfig.list}
 onBack={() => navigate('/references')}
 breadcrumbs={[
 { label: 'Справочники', to: '/references' },
 { label: 'Название' },
 ]}
 />
 )
}


## Шаг 3: Detail-страница

Создать frontend/src/pages/EntityDetailPage.tsx:
typescript
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { DetailPageShell } from '../components/DetailPageShell'
import { apiFetch } from '../lib/http'

export function EntityDetailPage() {
 const { entityId } = useParams()
 const [entity, setEntity] = useState(null)
 
 useEffect(() => {
 apiFetch(`/api/v1/.../${entityId}`)
 .then(r => r.json())
 .then(setEntity)
 }, [entityId])

 return (
 <DetailPageShell
 title={entity?.name}
 breadcrumbs={[
 { label: 'Справочники', to: '/references' },
 { label: 'Название', to: '/reference/entities' },
 { label: `#${entityId}` },
 ]}
 >
 {/* поля */}
 </DetailPageShell>
 )
}


## Шаг 4: Маршрут

В App.tsx добавить:
typescript
<Route path="/reference/entities" element={<EntitiesPage />} />
<Route path="/reference/entities/:entityId" element={<EntityDetailPage />} />


## Шаг 5: Справочники

В ReferencesPage.tsx добавить карточку в группу.
