import { GenericDetailPage } from './GenericDetailPage'
import type { ListPageConfig } from '../features/entity-system/types'

type Props<Row extends { id: number }> = {
  config: ListPageConfig<Row>
}

export function GenericDetailFromConfig<Row extends { id: number }>({ config }: Props<Row>) {
  const fields = (config.columns ?? []).map((col) => ({
    key: col.id,
    label: col.label,
    type:
      col.type === 'bool'
        ? ('bool' as const)
        : col.type === 'number'
          ? ('number' as const)
          : col.type === 'date' || col.type === 'datetime'
            ? ('date' as const)
            : ('text' as const),
  }))

  return (
    <GenericDetailPage
      title={config.title}
      apiUrl={config.apiUrl}
      backHref={config.listPath ?? '/'}
      backLabel={`← ${config.title}`}
      fields={fields}
    />
  )
}
