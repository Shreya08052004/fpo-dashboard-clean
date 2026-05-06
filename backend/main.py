from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import random
from datetime import datetime, timedelta

app = FastAPI(title="FPO Dashboard API", version="1.0.0")

# ✅ CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://fpo-dashboard-clean.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ HOME ROUTE
@app.get("/")
def home():
    return {"message": "Backend is running 🚀"}


# ─── DATA ─────────────────────────────────────────────
farmers = [
    {"id": f"F{str(i).zfill(3)}", "name": f"Farmer {i}", "village": f"Village {i}", "crop": "Wheat",
     "land_acres": random.uniform(1, 10), "income": random.randint(50000, 200000), "status": "Active"}
    for i in range(1, 21)
]

crops_data = {
    "Wheat": {"price_per_qtl": 2275},
    "Rice": {"price_per_qtl": 2183},
}

transactions = [
    {
        "id": f"T{i}",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "crop": "Wheat",
        "quantity_qtl": random.randint(10, 100),
        "total": random.randint(10000, 50000)
    }
    for i in range(1, 21)
]


# ─── API ROUTES ───────────────────────────────────────

@app.get("/api/summary")
def get_summary():
    return {
        "total_farmers": len(farmers),
        "active_farmers": len(farmers),
        "total_land_acres": sum(f["land_acres"] for f in farmers),
        "total_sales": sum(t["total"] for t in transactions),
        "avg_income": int(sum(f["income"] for f in farmers) / len(farmers)),
        "total_transactions": len(transactions),
        "crops_cultivated": len(crops_data),
        "villages_covered": len(farmers),
    }


@app.get("/api/farmers")
def get_farmers():
    return {"farmers": farmers}


@app.get("/api/transactions")
def get_transactions():
    return {"transactions": transactions}


@app.get("/api/crops")
def get_crops():
    return {"crops": [{"name": k, **v} for k, v in crops_data.items()]}


@app.get("/api/analytics/monthly-sales")
def monthly_sales():
    return {"data": [{"month": "Jan", "sales": 50000}, {"month": "Feb", "sales": 70000}]}


@app.get("/api/analytics/crop-distribution")
def crop_distribution():
    return {"data": [{"crop": "Wheat", "count": 10}, {"crop": "Rice", "count": 10}]}


@app.get("/api/analytics/village-stats")
def village_stats():
    return {"data": []}


@app.get("/api/analytics/income-trend")
def income_trend():
    return {"data": []}


@app.get("/api/weather")
def get_weather():
    return {"temp": 30}


@app.get("/api/alerts")
def get_alerts():
    return {"alerts": []}


class FarmerCreate(BaseModel):
    name: str
    village: str
    crop: str
    land_acres: float


@app.post("/api/farmers")
def create_farmer(farmer: FarmerCreate):
    new_farmer = {
        "id": f"F{len(farmers)+1}",
        **farmer.dict()
    }
    farmers.append(new_farmer)
    return {"success": True, "farmer": new_farmer}