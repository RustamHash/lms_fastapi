import { getAccessToken } from './token'

/** Запросы к защищённому API: Bearer из sessionStorage. */
export function apiFetch(input: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers)
  const t = getAccessToken()
  if (t) headers.set('Authorization', `Bearer ${t}`)
  if (
    init.body &&
    typeof init.body === 'string' &&
    !headers.has('Content-Type')
  ) {
    headers.set('Content-Type', 'application/json')
  }
  return fetch(input, { ...init, headers })
}
