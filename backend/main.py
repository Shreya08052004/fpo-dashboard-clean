from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import random
from datetime import datetime, timedelta

app = FastAPI(title="FPO Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://fpo-dashboard-clean.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "FPO Backend is running 🚀"}


# ─── DATA ─────────────────────────────────────────────────────────

FARMER_NAMES = [
    ("Ramesh Kumar","Sitapur","Wheat"),("Sunita Devi","Barabanki","Rice"),
    ("Mohan Singh","Hardoi","Sugarcane"),("Priya Sharma","Unnao","Mustard"),
    ("Vijay Yadav","Lakhimpur","Potato"),("Kavita Patel","Rae Bareli","Maize"),
    ("Raju Verma","Sultanpur","Wheat"),("Anita Mishra","Faizabad","Rice"),
    ("Dinesh Gupta","Gonda","Sugarcane"),("Meena Chauhan","Bahraich","Dal"),
    ("Arun Tiwari","Shravasti","Wheat"),("Seema Rani","Balrampur","Mustard"),
    ("Prakash Joshi","Basti","Rice"),("Urmila Singh","Gorakhpur","Potato"),
    ("Santosh Kumar","Deoria","Maize"),("Pushpa Devi","Kushinagar","Wheat"),
    ("Harishankar Pal","Maharajganj","Sugarcane"),("Geeta Devi","Siddharthnagar","Dal"),
    ("Ramkishore Yadav","Sant Kabir Nagar","Rice"),("Sharda Singh","Ambedkar Nagar","Wheat"),
]

farmers = [
    {
        "id": f"F{str(i+1).zfill(3)}",
        "name": name,
        "village": village,
        "crop": crop,
        "land_acres": round(random.uniform(1.5, 12.0), 1),
        "income": random.randint(45000, 280000),
        "status": "Inactive" if i % 5 == 4 else "Active",
        "joined": (datetime.now() - timedelta(days=random.randint(30, 900))).strftime("%Y-%m-%d"),
    }
    for i, (name, village, crop) in enumerate(FARMER_NAMES)
]

crops_data = {
    "Wheat":     {"price_per_qtl": 2275, "production_qtl": 1200, "area_ha": 450, "msp": 2275},
    "Rice":      {"price_per_qtl": 2183, "production_qtl": 980,  "area_ha": 380, "msp": 2183},
    "Sugarcane": {"price_per_qtl": 370,  "production_qtl": 8500, "area_ha": 320, "msp": 370},
    "Mustard":   {"price_per_qtl": 5650, "production_qtl": 420,  "area_ha": 180, "msp": 5650},
    "Potato":    {"price_per_qtl": 1200, "production_qtl": 2100, "area_ha": 140, "msp": 900},
    "Maize":     {"price_per_qtl": 2090, "production_qtl": 650,  "area_ha": 210, "msp": 2090},
    "Dal":       {"price_per_qtl": 6600, "production_qtl": 280,  "area_ha": 120, "msp": 6200},
}

CROP_KEYS = list(crops_data.keys())
BUYERS = ["Govt Mandi", "Private Trader", "Export House", "Direct Consumer", "FPO Store"]
TX_STATUS = ["Completed", "Completed", "Completed", "Pending", "Processing"]

transactions = []
for i in range(60):
    crop = CROP_KEYS[i % len(CROP_KEYS)]
    qty = random.randint(10, 200)
    price = crops_data[crop]["price_per_qtl"] * random.uniform(0.95, 1.15)
    date = (datetime.now() - timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d")
    transactions.append({
        "id": f"T{str(i+1).zfill(4)}",
        "date": date,
        "farmer_id": f"F{str(random.randint(1,20)).zfill(3)}",
        "crop": crop,
        "quantity_qtl": qty,
        "price_per_qtl": round(price, 2),
        "total": round(qty * price, 2),
        "buyer": BUYERS[i % len(BUYERS)],
        "status": TX_STATUS[i % len(TX_STATUS)],
    })
transactions.sort(key=lambda x: x["date"], reverse=True)


# ─── ROUTES ───────────────────────────────────────────────────────

@app.get("/api/summary")
def get_summary():
    active = sum(1 for f in farmers if f["status"] == "Active")
    completed = [t for t in transactions if t["status"] == "Completed"]
    total_sales = sum(t["total"] for t in completed)
    return {
        "total_farmers": len(farmers),
        "active_farmers": active,
        "total_land_acres": round(sum(f["land_acres"] for f in farmers), 1),
        "total_sales": round(total_sales, 2),
        "avg_income": round(sum(f["income"] for f in farmers) / len(farmers)),
        "total_transactions": len(transactions),
        "crops_cultivated": len(crops_data),
        "villages_covered": len(set(f["village"] for f in farmers)),
    }


@app.get("/api/farmers")
def get_farmers(search: Optional[str] = None, status: Optional[str] = None, crop: Optional[str] = None):
    result = farmers[:]
    if search:
        result = [f for f in result if search.lower() in f["name"].lower() or search.lower() in f["village"].lower()]
    if status and status != "All":
        result = [f for f in result if f["status"] == status]
    if crop and crop != "All":
        result = [f for f in result if f["crop"] == crop]
    return {"farmers": result, "total": len(result)}


@app.get("/api/transactions")
def get_transactions(page: int = 1, limit: int = 12, crop: Optional[str] = None, status: Optional[str] = None):
    result = transactions[:]
    if crop and crop != "All":
        result = [t for t in result if t["crop"] == crop]
    if status and status != "All":
        result = [t for t in result if t["status"] == status]
    total = len(result)
    start = (page - 1) * limit
    return {"transactions": result[start:start+limit], "total": total, "pages": (total + limit - 1) // limit}


@app.get("/api/crops")
def get_crops():
    return {"crops": [{"name": k, **v} for k, v in crops_data.items()]}


@app.get("/api/analytics/monthly-sales")
def monthly_sales():
    monthly = {}
    for t in transactions:
        if t["status"] == "Completed":
            month = t["date"][:7]
            monthly[month] = monthly.get(month, 0) + t["total"]
    sorted_months = sorted(monthly.items())[-6:]
    return {"data": [{"month": m, "sales": round(v, 2)} for m, v in sorted_months]}


@app.get("/api/analytics/crop-distribution")
def crop_distribution():
    dist = {}
    for f in farmers:
        dist[f["crop"]] = dist.get(f["crop"], 0) + 1
    return {"data": [{"crop": k, "count": v, "percentage": round(v/len(farmers)*100, 1)} for k, v in dist.items()]}


@app.get("/api/analytics/village-stats")
def village_stats():
    stats = {}
    for f in farmers:
        v = f["village"]
        if v not in stats:
            stats[v] = {"village": v, "farmers": 0, "total_land": 0.0, "incomes": []}
        stats[v]["farmers"] += 1
        stats[v]["total_land"] += f["land_acres"]
        stats[v]["incomes"].append(f["income"])
    result = [
        {
            "village": v,
            "farmers": s["farmers"],
            "total_land": round(s["total_land"], 1),
            "avg_income": round(sum(s["incomes"]) / len(s["incomes"])),
        }
        for v, s in stats.items()
    ]
    return {"data": sorted(result, key=lambda x: x["farmers"], reverse=True)}


@app.get("/api/analytics/income-trend")
def income_trend():
    data = []
    for i in range(12):
        month = (datetime.now() - timedelta(days=30 * (11 - i))).strftime("%Y-%m")
        base = 160000 + i * 3000 + random.randint(-8000, 12000)
        data.append({
            "month": month,
            "avg_income": base,
            "min_income": base - random.randint(20000, 50000),
            "max_income": base + random.randint(20000, 70000),
        })
    return {"data": data}


@app.get("/api/weather")
def get_weather():
    conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Light Rain"]
    return {
        "location": "Lucknow, UP",
        "temp": random.randint(28, 38),
        "humidity": random.randint(55, 80),
        "condition": random.choice(conditions),
        "wind_kmh": random.randint(10, 25),
        "forecast": [
            {"day": "Today",    "high": 36, "low": 26, "condition": "Sunny"},
            {"day": "Tomorrow", "high": 34, "low": 25, "condition": "Partly Cloudy"},
            {"day": "Wed",      "high": 31, "low": 24, "condition": "Light Rain"},
            {"day": "Thu",      "high": 33, "low": 25, "condition": "Cloudy"},
            {"day": "Fri",      "high": 35, "low": 26, "condition": "Sunny"},
        ],
    }


@app.get("/api/alerts")
def get_alerts():
    return {"alerts": [
        {"id": 1, "type": "warning", "title": "Wheat MSP Updated",    "message": "Minimum Support Price for Wheat raised to ₹2,275/quintal",      "time": "2 hours ago"},
        {"id": 2, "type": "info",    "title": "New Subsidy Available", "message": "PM Kisan 17th installment to be released next week",             "time": "5 hours ago"},
        {"id": 3, "type": "success", "title": "Procurement Drive",     "message": "Government procurement camp at Hardoi Mandi on 10th May",        "time": "1 day ago"},
        {"id": 4, "type": "danger",  "title": "Pest Alert",            "message": "Fall Armyworm spotted in Lakhimpur region – take precautions",   "time": "2 days ago"},
        {"id": 5, "type": "info",    "title": "Loan Disbursement",     "message": "KCC loan applications approved for 12 farmers",                  "time": "3 days ago"},
    ]}


class FarmerCreate(BaseModel):
    name: str
    village: str
    crop: str
    land_acres: float
    income: Optional[int] = 0

@app.post("/api/farmers")
def create_farmer(farmer: FarmerCreate):
    new_farmer = {
        "id": f"F{str(len(farmers)+1).zfill(3)}",
        "name": farmer.name,
        "village": farmer.village,
        "crop": farmer.crop,
        "land_acres": farmer.land_acres,
        "income": farmer.income,
        "status": "Active",
        "joined": datetime.now().strftime("%Y-%m-%d"),
    }
    farmers.append(new_farmer)
    return {"success": True, "farmer": new_farmer}