const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const NORMALIZED_API_BASE_URL = API_BASE_URL.replace(/\/+$/, '')

async function readJson(response) {
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload.detail || 'Request failed')
  }
  return payload
}

function buildApiUrl(path) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${NORMALIZED_API_BASE_URL}${normalizedPath}`
}

export async function analyzeWafer(file) {
  const body = new FormData()
  body.append('file', file)

  const response = await fetch(buildApiUrl('/analyze'), {
    method: 'POST',
    body,
  })

  return readJson(response)
}

export async function fetchHistory(limit = 100) {
  const response = await fetch(buildApiUrl(`/history?limit=${limit}`))
  return readJson(response)
}

export async function fetchAnalytics(limit = 500) {
  const response = await fetch(buildApiUrl(`/analytics?limit=${limit}`))
  return readJson(response)
}

export async function fetchOverview() {
  const response = await fetch(buildApiUrl('/overview'))
  return readJson(response)
}