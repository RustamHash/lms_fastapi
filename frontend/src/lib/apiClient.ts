import { getAccessToken } from './token'

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail)
    this.name = 'ApiError'
  }
}

function getHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  const token = getAccessToken()
  if (token) headers['Authorization'] = `Bearer ${token}`
  return headers
}

async function parseError(res: Response): Promise<string> {
  try {
    const data = await res.json() as { detail?: string; message?: string }
    return data.detail ?? data.message ?? `HTTP ${res.status}`
  } catch {
    return `HTTP ${res.status}`
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (res.status === 401) {
    sessionStorage.removeItem('sslogistics_access_token')
    window.location.href = '/login'
    throw new ApiError(401, 'Необходима авторизация')
  }
  if (!res.ok) {
    throw new ApiError(res.status, await parseError(res))
  }
  if (res.status === 204) {
    return undefined as T
  }
  return res.json() as Promise<T>
}

export const apiClient = {
  async get<T>(url: string, signal?: AbortSignal): Promise<T> {
    const res = await fetch(url, {
      headers: getHeaders(),
      signal,
    })
    return handleResponse<T>(res)
  },

  async post<T>(url: string, body?: unknown, signal?: AbortSignal): Promise<T> {
    const res = await fetch(url, {
      method: 'POST',
      headers: getHeaders(),
      body: body ? JSON.stringify(body) : undefined,
      signal,
    })
    return handleResponse<T>(res)
  },

  async put<T>(url: string, body: unknown, signal?: AbortSignal): Promise<T> {
    const res = await fetch(url, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(body),
      signal,
    })
    return handleResponse<T>(res)
  },

  async patch<T>(url: string, body: unknown, signal?: AbortSignal): Promise<T> {
    const res = await fetch(url, {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify(body),
      signal,
    })
    return handleResponse<T>(res)
  },

  async delete(url: string, signal?: AbortSignal): Promise<void> {
    const res = await fetch(url, {
      method: 'DELETE',
      headers: getHeaders(),
      signal,
    })
    await handleResponse<void>(res)
  },
}
