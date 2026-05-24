// ─── 100% Frontend Data — No Backend Needed ──────────────────────
// This works perfectly on Vercel with zero CORS issues

const delay = (ms = 400) => new Promise(r => setTimeout(r, ms))

const rnd = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min
const rndF = (min, max) => +(Math.random() * (max - min) + min).toFixed(1)

const FARMER_NAMES = [
  ["Ramesh Kumar","Sitapur","Wheat"],["Sunita Devi","Barabanki","Rice"],
  ["Mohan Singh","Hardoi","Sugarcane"],["Priya Sharma","Unnao","Mustard"],
  ["Vijay Yadav","Lakhimpur","Potato"],["Kavita Patel","Rae Bareli","Maize"],
  ["Raju Verma","Sultanpur","Wheat"],["Anita Mishra","Faizabad","Rice"],
  ["Dinesh Gupta","Gonda","Sugarcane"],["Meena Chauhan","Bahraich","Dal"],
  ["Arun Tiwari","Shravasti","Wheat"],["Seema Rani","Balrampur","Mustard"],
  ["Prakash Joshi","Basti","Rice"],["Urmila Singh","Gorakhpur","Potato"],
  ["Santosh Kumar","Deoria","Maize"],["Pushpa Devi","Kushinagar","Wheat"],
  ["Harishankar Pal","Maharajganj","Sugarcane"],["Geeta Devi","Siddharthnagar","Dal"],
  ["Ramkishore Yadav","Sant Kabir Nagar","Rice"],["Sharda Singh","Ambedkar Nagar","Wheat"],
]

const CROPS_DATA = {
  Wheat:     { price_per_qtl: 2275, production_qtl: 1200, area_ha: 450, msp: 2275 },
  Rice:      { price_per_qtl: 2183, production_qtl: 980,  area_ha: 380, msp: 2183 },
  Sugarcane: { price_per_qtl: 370,  production_qtl: 8500, area_ha: 320, msp: 370  },
  Mustard:   { price_per_qtl: 5650, production_qtl: 420,  area_ha: 180, msp: 5650 },
  Potato:    { price_per_qtl: 1200, production_qtl: 2100, area_ha: 140, msp: 900  },
  Maize:     { price_per_qtl: 2090, production_qtl: 650,  area_ha: 210, msp: 2090 },
  Dal:       { price_per_qtl: 6600, production_qtl: 280,  area_ha: 120, msp: 6200 },
}

const CROP_KEYS = Object.keys(CROPS_DATA)
const BUYERS = ['Govt Mandi','Private Trader','Export House','Direct Consumer','FPO Store']
const TX_STATUS = ['Completed','Completed','Completed','Pending','Processing']

// Build data once when page loads
const farmers = FARMER_NAMES.map(([name, village, crop], i) => ({
  id: `F${String(i + 1).padStart(3, '0')}`,
  name, village, crop,
  land_acres: rndF(1.5, 12),
  income: rnd(45000, 280000),
  status: i % 5 === 4 ? 'Inactive' : 'Active',
  joined: new Date(Date.now() - rnd(30, 900) * 86400000).toISOString().slice(0, 10),
}))

const transactions = Array.from({ length: 60 }, (_, i) => {
  const crop = CROP_KEYS[i % CROP_KEYS.length]
  const qty = rnd(10, 200)
  const price = CROPS_DATA[crop].price_per_qtl * (0.95 + Math.random() * 0.2)
  const date = new Date(Date.now() - rnd(0, 180) * 86400000).toISOString().slice(0, 10)
  return {
    id: `T${String(i + 1).padStart(4, '0')}`,
    date,
    farmer_id: `F${String(rnd(1, 20)).padStart(3, '0')}`,
    crop,
    quantity_qtl: qty,
    price_per_qtl: +price.toFixed(2),
    total: +(qty * price).toFixed(2),
    buyer: BUYERS[i % BUYERS.length],
    status: TX_STATUS[i % TX_STATUS.length],
  }
}).sort((a, b) => b.date.localeCompare(a.date))

export const api = {
  async summary() {
    await delay(300)
    const active = farmers.filter(f => f.status === 'Active').length
    const totalSales = transactions.filter(t => t.status === 'Completed').reduce((s, t) => s + t.total, 0)
    return {
      total_farmers: farmers.length,
      active_farmers: active,
      total_land_acres: +farmers.reduce((s, f) => s + f.land_acres, 0).toFixed(1),
      total_sales: +totalSales.toFixed(2),
      avg_income: Math.round(farmers.reduce((s, f) => s + f.income, 0) / farmers.length),
      total_transactions: transactions.length,
      crops_cultivated: CROP_KEYS.length,
      villages_covered: new Set(farmers.map(f => f.village)).size,
    }
  },

  async farmers({ search = '', status = '', crop = '' } = {}) {
    await delay(300)
    let result = [...farmers]
    if (search) result = result.filter(f =>
      f.name.toLowerCase().includes(search.toLowerCase()) ||
      f.village.toLowerCase().includes(search.toLowerCase())
    )
    if (status && status !== 'All') result = result.filter(f => f.status === status)
    if (crop && crop !== 'All') result = result.filter(f => f.crop === crop)
    return { farmers: result, total: result.length }
  },

  async createFarmer(data) {
    await delay(600)
    const newF = {
      id: `F${String(farmers.length + 1).padStart(3, '0')}`,
      ...data,
      status: 'Active',
      joined: new Date().toISOString().slice(0, 10),
    }
    farmers.push(newF)
    return { success: true, farmer: newF }
  },

  async crops() {
    await delay(200)
    return { crops: CROP_KEYS.map(name => ({ name, ...CROPS_DATA[name] })) }
  },

  async transactions({ page = 1, limit = 12, crop = '', status = '' } = {}) {
    await delay(300)
    let result = [...transactions]
    if (crop && crop !== 'All') result = result.filter(t => t.crop === crop)
    if (status && status !== 'All') result = result.filter(t => t.status === status)
    const total = result.length
    const start = (page - 1) * limit
    return { transactions: result.slice(start, start + limit), total, pages: Math.ceil(total / limit) }
  },

  async monthlySales() {
    await delay(200)
    const map = {}
    transactions.filter(t => t.status === 'Completed').forEach(t => {
      const m = t.date.slice(0, 7)
      map[m] = (map[m] || 0) + t.total
    })
    const data = Object.entries(map).sort().slice(-6).map(([month, sales]) => ({ month, sales: +sales.toFixed(2) }))
    return { data }
  },

  async cropDistribution() {
    await delay(200)
    const dist = {}
    farmers.forEach(f => { dist[f.crop] = (dist[f.crop] || 0) + 1 })
    return {
      data: Object.entries(dist).map(([crop, count]) => ({
        crop, count, percentage: +((count / farmers.length) * 100).toFixed(1),
      }))
    }
  },

  async villageStats() {
    await delay(200)
    const map = {}
    farmers.forEach(f => {
      if (!map[f.village]) map[f.village] = { village: f.village, farmers: 0, total_land: 0, incomes: [] }
      map[f.village].farmers++
      map[f.village].total_land += f.land_acres
      map[f.village].incomes.push(f.income)
    })
    const data = Object.values(map).map(v => ({
      village: v.village,
      farmers: v.farmers,
      total_land: +v.total_land.toFixed(1),
      avg_income: Math.round(v.incomes.reduce((a, b) => a + b, 0) / v.incomes.length),
    })).sort((a, b) => b.farmers - a.farmers)
    return { data }
  },

  async incomeTrend() {
    await delay(200)
    const data = Array.from({ length: 12 }, (_, i) => {
      const d = new Date()
      d.setMonth(d.getMonth() - (11 - i))
      const month = d.toISOString().slice(0, 7)
      const base = 160000 + i * 3000 + rnd(-8000, 12000)
      return { month, avg_income: base, min_income: base - rnd(20000, 50000), max_income: base + rnd(20000, 70000) }
    })
    return { data }
  },

  async weather() {
    await delay(150)
    return {
      location: 'Lucknow, UP',
      temp: rnd(28, 38),
      humidity: rnd(55, 80),
      condition: ['Sunny','Partly Cloudy','Cloudy','Light Rain'][rnd(0, 3)],
      wind_kmh: rnd(10, 25),
      forecast: [
        { day: 'Today',    high: 36, low: 26, condition: 'Sunny' },
        { day: 'Tomorrow', high: 34, low: 25, condition: 'Partly Cloudy' },
        { day: 'Wed',      high: 31, low: 24, condition: 'Light Rain' },
        { day: 'Thu',      high: 33, low: 25, condition: 'Cloudy' },
        { day: 'Fri',      high: 35, low: 26, condition: 'Sunny' },
      ],
    }
  },

  async alerts() {
    await delay(150)
    return {
      alerts: [
        { id: 1, type: 'warning', title: 'Wheat MSP Updated',    message: 'Minimum Support Price for Wheat raised to ₹2,275/quintal',     time: '2 hours ago' },
        { id: 2, type: 'info',    title: 'New Subsidy Available', message: 'PM Kisan 17th installment to be released next week',            time: '5 hours ago' },
        { id: 3, type: 'success', title: 'Procurement Drive',     message: 'Government procurement camp at Hardoi Mandi on 10th May',      time: '1 day ago' },
        { id: 4, type: 'danger',  title: 'Pest Alert',            message: 'Fall Armyworm spotted in Lakhimpur region – take precautions', time: '2 days ago' },
        { id: 5, type: 'info',    title: 'Loan Disbursement',     message: 'KCC loan applications approved for 12 farmers',                time: '3 days ago' },
      ]
    }
  },
}
