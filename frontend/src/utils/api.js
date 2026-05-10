const BASE = 'https://fpo-backend.onrender.com/api'

async function request(path, opts = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...opts.headers },
    ...opts,
  })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

export const api = {
  summary:          ()       => request('/summary'),
  farmers:          (p = {}) => {
    const q = new URLSearchParams(p).toString()
    return request(`/farmers${q ? '?' + q : ''}`)
  },
  createFarmer:     (data)   => request('/farmers', { method: 'POST', body: JSON.stringify(data) }),
  crops:            ()       => request('/crops'),
  transactions:     (p = {}) => {
    const q = new URLSearchParams(p).toString()
    return request(`/transactions${q ? '?' + q : ''}`)
  },
  monthlySales:     ()       => request('/analytics/monthly-sales'),
  cropDistribution: ()       => request('/analytics/crop-distribution'),
  villageStats:     ()       => request('/analytics/village-stats'),
  incomeTrend:      ()       => request('/analytics/income-trend'),
  weather:          ()       => request('/weather'),
  alerts:           ()       => request('/alerts'),
}