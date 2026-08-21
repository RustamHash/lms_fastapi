import { GenericDetailPage } from '../components/GenericDetailPage'

export function FileDetailPage() {
  return (
    <GenericDetailPage
      title="Файл"
      apiUrl="/api/v1/files"
      backHref="/files"
      backLabel="← К файлам"
      fields={[
        { key: 'id', label: 'ID', type: 'number' as const },
        { key: 'file_path', label: 'Путь', type: 'text' as const },
        { key: 'file_type', label: 'Тип', type: 'text' as const },
        { key: 'original_name', label: 'Имя', type: 'text' as const },
        { key: 'size', label: 'Размер', type: 'number' as const },
        { key: 'mime_type', label: 'MIME', type: 'text' as const },
      ]}
    />
  )
}
