// Base URL is empty so requests go through the Vite dev proxy (/api → http://localhost:8000).
// In production, set VITE_API_BASE in your .env to the deployed backend URL.
const BASE = import.meta.env.VITE_API_BASE ?? ''

/**
 * Thin fetch wrapper.
 *
 * For 422 Unprocessable Entity (FastAPI / Pydantic validation errors) the
 * thrown Error has a `fieldErrors` property — a plain object mapping field
 * name → human-readable message — so the form can display them inline.
 *
 * For all other errors the thrown Error has a plain `message` string.
 */
async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))

    // FastAPI emits 422 with detail as an array of loc/msg objects.
    if (res.status === 422 && Array.isArray(body.detail)) {
      const fieldErrors = {}
      for (const err of body.detail) {
        // loc is ["body", "field_name"] or ["body", "field_name", index]
        const field = err.loc.at(-1)
        if (typeof field === 'string' && field !== 'body') {
          fieldErrors[field] = err.msg
            .replace(/^Value error,\s*/i, '') // strip Pydantic v2 prefix
        }
      }
      const error = new Error('Validation failed')
      error.fieldErrors = fieldErrors
      throw error
    }

    throw new Error(
      typeof body.detail === 'string' ? body.detail : 'Request failed',
    )
  }

  return res.json()
}

export const api = {
  /** Fetch all active projects for the multi-select dropdown. */
  getProjects: () => request('/api/projects/'),

  /** Load an employee profile by their UUID (stored in localStorage). */
  getEmployee: (id) => request(`/api/employees/${id}`),

  /** Look up an employee by email — used when a returning user enters their address. */
  getEmployeeByEmail: (email) =>
    request(`/api/employees/by-email/${encodeURIComponent(email)}`),

  /** Register a new employee profile. Returns 409 if email already exists. */
  createEmployee: (data) =>
    request('/api/employees/', { method: 'POST', body: JSON.stringify(data) }),

  /** Update an existing employee profile and replace project selections. */
  updateEmployee: (id, data) =>
    request(`/api/employees/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
}
