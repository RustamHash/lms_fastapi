import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { EntityListPage } from '../features/entity-system/EntityListPage'
import { tasksConfig } from '../features/tasks/config'

const TASK_TYPES = [
  { value: 'all', label: 'Все задания' },
  { value: 'picking', label: 'Отбор' },
  { value: 'receiving', label: 'Приёмка' },
  { value: 'putaway', label: 'Размещение' },
  { value: 'shipping', label: 'Отгрузка' },
  { value: 'movement', label: 'Перемещение' },
]

function todayString(): string {
  const d = new Date()
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

export function TasksPage() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const activeType = searchParams.get('task_type') || 'all'
  const dateFrom = searchParams.get('date_from') || todayString()
  const dateTo = searchParams.get('date_to') || ''

  function handleTypeChange(event: React.ChangeEvent<HTMLSelectElement>) {
    const type = event.target.value
    if (type === 'all') {
      searchParams.delete('task_type')
    } else {
      searchParams.set('task_type', type)
    }
    setSearchParams(searchParams)
  }

  function handleDateFromChange(event: React.ChangeEvent<HTMLInputElement>) {
    const value = event.target.value
    if (value) {
      searchParams.set('date_from', value)
    } else {
      searchParams.delete('date_from')
    }
    setSearchParams(searchParams)
  }

  function handleDateToChange(event: React.ChangeEvent<HTMLInputElement>) {
    const value = event.target.value
    if (value) {
      searchParams.set('date_to', value)
    } else {
      searchParams.delete('date_to')
    }
    setSearchParams(searchParams)
  }

  const params = new URLSearchParams()
  if (activeType !== 'all') params.set('task_type', activeType)
  if (dateFrom) params.set('date_from', dateFrom)
  if (dateTo) params.set('date_to', dateTo)
  
  const apiUrl = `/api/v1/warehouse/tasks${params.toString() ? `?${params.toString()}` : ''}`

  return (
    <section className="app-card app-card--wide">
      <div className="detail-nav detail-nav--with-title">
        <button type="button" className="detail-nav__back" onClick={() => navigate('/')}>
          ← Назад
        </button>
        <nav className="breadcrumbs" aria-label="Хлебные крошки">
          <span className="breadcrumbs__item">
            <Link to="/" className="breadcrumbs__link">Главная</Link>
            <span className="breadcrumbs__sep">/</span>
          </span>
          <span className="breadcrumbs__item">
            <span className="breadcrumbs__current">Задания</span>
          </span>
        </nav>
        <h1 className="detail-nav__title">Задания</h1>
      </div>

      <div className="task-filter">
        <select 
          className="task-filter__select"
          value={activeType}
          onChange={handleTypeChange}
        >
          {TASK_TYPES.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
        
        <label className="task-filter__date">
          <span>От:</span>
          <input 
            type="date" 
            className="task-filter__date-input"
            value={dateFrom}
            onChange={handleDateFromChange}
          />
        </label>
        
        <label className="task-filter__date">
          <span>До:</span>
          <input 
            type="date" 
            className="task-filter__date-input"
            value={dateTo}
            onChange={handleDateToChange}
          />
        </label>
      </div>

      <EntityListPage
        key={`${activeType}-${dateFrom}-${dateTo}`}
        config={{
          ...tasksConfig,
          title: '',
          apiUrl,
        }}
        onBack={undefined}
        breadcrumbs={undefined}
      />
    </section>
  )
}
