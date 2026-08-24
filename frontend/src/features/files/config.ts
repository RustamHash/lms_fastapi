import type { ListPageConfig } from '../entity-system/types'

type FileRow = {
  id: number
  file_path: string
  file_type: string
  original_name: string
  size: number
  mime_type: string
  uploaded_by_id: number | null
}

export const filesConfig: ListPageConfig<FileRow> = {
  entityKey: 'files',
  title: 'Файлы',
  apiUrl: '/api/v1/files',
  columns: [
    { id: 'id', label: 'ID', type: 'number' },
    { id: 'original_name', label: 'Имя файла', type: 'text' },
    { id: 'file_type', label: 'Тип', type: 'text' },
    { id: 'size', label: 'Размер', type: 'number' },
    { id: 'mime_type', label: 'MIME тип', type: 'text' },
  ],
  filters: [
    { id: 'original_name', type: 'text', label: 'Имя файла' },
    { id: 'file_type', type: 'text', label: 'Тип' },
  ],

  columnOverrides: {
    id: { href: (row) => `/reference/files/${row.id}` },
  },
}