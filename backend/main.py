from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import random
from datetime import datetime, timedelta

app = FastAPI(title="FPO Dashboard API", version="1.0.0")

# ✅ UPDATED CORS (IMPORTANT)
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


# ─── Mock Data Store ───────────────────────────────────────────────
farmers = [
    {"id": f"F{str(i).zfill(3)}", "name": n, "village": v, "crop": c, "land_acres": round(random.uniform(1.5, 12.0), 1), "income": random.randint(45000, 280000), "status": random.choice(["Active", "Inactive"]), "joined": (datetime.now() - timedelta(days=random.randint(30, 900))).strftime("%Y-%m-%d")}
    for i, (n, v, c) in enumerate([
        ("Ramesh Kumar", "Sitapur", "Wheat"), ("Sunita Devi", "Barabanki", "Rice"),
        ("Mohan Singh", "Hardoi", "Sugarcane"), ("Priya Sharma", "Unnao", "Mustard"),
        ("Vijay Yadav", "Lakhimpur", "Potato"), ("Kavita Patel", "Rae Bareli", "Maize"),
    ], 1)
]

crops_data = {
    "Wheat": {"price_per_qtl": 2275},
    "Rice": {"price_per_qtl": 2183},
}

transactions = []
for i in range(20):
    crop = random.choice(list(crops_data.keys()))
    qty = random.randint(10, 100)
    price = crops_data[crop]["price_per_qtl"]

    transactions.append({
        "id": f"T{str(i+1).zfill(3)}",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "crop": crop,
        "quantity_qtl": qty,
        "total": qty * price
    })


# ─── API Routes ────────────────────────────────────────────────────

@app.get("/api/summary")
def get_summary():
    return {
        "total_farmers": len(farmers),
        "total_transactions": len(transactions)
    }


@app.get("/api/farmers")
def get_farmers():
    return {"farmers": farmers}


@app.get("/api/transactions")
def get_transactions():
    return {"transactions": transactions}


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