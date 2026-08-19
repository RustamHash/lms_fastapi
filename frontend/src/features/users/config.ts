import type { ListPageConfig } from '../entity-list/types'

type UserRow = {
  id: number
  username: string
  phone: string
  email: string
  is_superuser: boolean
  is_active: boolean
}

export const usersConfig: ListPageConfig<UserRow> = {
  entityKey: 'users',
  title: 'Пользователи',
  apiUrl: '/api/v1/users',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'username', label: 'Имя пользователя', type: 'text' },
    { id: 'email', label: 'Email', type: 'text' },
    { id: 'phone', label: 'Телефон', type: 'text' },
    { id: 'is_superuser', label: 'Суперпользователь', type: 'bool' },
    { id: 'is_active', label: 'Активен', type: 'bool' },
  ],
  filters: [
    { id: 'username', type: 'text', label: 'Имя пользователя' },
    { id: 'email', type: 'text', label: 'Email' },
  ],
}
