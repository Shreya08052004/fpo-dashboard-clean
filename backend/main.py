from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import random
from datetime import datetime, timedelta
import json

app = FastAPI(title="FPO Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ ADDED THIS ROUTE
@app.get("/")
def home():
    return {"message": "Backend is running 🚀"}


# ─── Mock Data Store ───────────────────────────────────────────────
farmers = [
    {"id": f"F{str(i).zfill(3)}", "name": n, "village": v, "crop": c, "land_acres": round(random.uniform(1.5, 12.0), 1), "income": random.randint(45000, 280000), "status": random.choice(["Active", "Active", "Active", "Inactive"]), "joined": (datetime.now() - timedelta(days=random.randint(30, 900))).strftime("%Y-%m-%d")}
    for i, (n, v, c) in enumerate([
        ("Ramesh Kumar", "Sitapur", "Wheat"), ("Sunita Devi", "Barabanki", "Rice"),
        ("Mohan Singh", "Hardoi", "Sugarcane"), ("Priya Sharma", "Unnao", "Mustard"),
        ("Vijay Yadav", "Lakhimpur", "Potato"), ("Kavita Patel", "Rae Bareli", "Maize"),
        ("Raju Verma", "Sultanpur", "Wheat"), ("Anita Mishra", "Faizabad", "Rice"),
        ("Dinesh Gupta", "Gonda", "Sugarcane"), ("Meena Chauhan", "Bahraich", "Dal"),
        ("Arun Tiwari", "Shravasti", "Wheat"), ("Seema Rani", "Balrampur", "Mustard"),
        ("Prakash Joshi", "Basti", "Rice"), ("Urmila Singh", "Gorakhpur", "Potato"),
        ("Santosh Kumar", "Deoria", "Maize"), ("Pushpa Devi", "Kushinagar", "Wheat"),
        ("Harishankar", "Maharajganj", "Sugarcane"), ("Geeta Pal", "Siddharthnagar", "Dal"),
        ("Ramkishore", "Sant Kabir Nagar", "Rice"), ("Sharda Devi", "Ambedkar Nagar", "Wheat"),
    ], 1)
]

crops_data = {
    "Wheat": {"price_per_qtl": 2275, "production_qtl": 1200, "area_ha": 450, "msp": 2275},
    "Rice": {"price_per_qtl": 2183, "production_qtl": 980, "area_ha": 380, "msp": 2183},
    "Sugarcane": {"price_per_qtl": 370, "production_qtl": 8500, "area_ha": 320, "msp": 370},
    "Mustard": {"price_per_qtl": 5650, "production_qtl": 420, "area_ha": 180, "msp": 5650},
    "Potato": {"price_per_qtl": 1200, "production_qtl": 2100, "area_ha": 140, "msp": 900},
    "Maize": {"price_per_qtl": 2090, "production_qtl": 650, "area_ha": 210, "msp": 2090},
    "Dal": {"price_per_qtl": 6600, "production_qtl": 280, "area_ha": 120, "msp": 6200},
}

transactions = []
for i in range(60):
    d = datetime.now() - timedelta(days=random.randint(0, 180))
    crop = random.choice(list(crops_data.keys()))
    qty = random.randint(10, 200)
    price = crops_data[crop]["price_per_qtl"] * random.uniform(0.95, 1.15)
    transactions.append({
        "id": f"T{str(i+1).zfill(4)}",
        "date": d.strftime("%Y-%m-%d"),
        "farmer_id": f"F{str(random.randint(1,20)).zfill(3)}",
        "crop": crop,
        "quantity_qtl": qty,
        "price_per_qtl": round(price, 2),
        "total": round(qty * price, 2),
        "buyer": random.choice(["Govt Mandi", "Private Trader", "Export House", "Direct Consumer", "FPO Store"]),
        "status": random.choice(["Completed", "Completed", "Completed", "Pending", "Processing"])
    })

transactions.sort(key=lambda x: x["date"], reverse=True)

# ─── API Routes ────────────────────────────────────────────────────

@app.get("/api/summary")
def get_summary():
    active = sum(1 for f in farmers if f["status"] == "Active")
    total_income = sum(f["income"] for f in farmers)
    total_land = sum(f["land_acres"] for f in farmers)
    completed_tx = [t for t in transactions if t["status"] == "Completed"]
    total_sales = sum(t["total"] for t in completed_tx)
    return {
        "total_farmers": len(farmers),
        "active_farmers": active,
        "total_land_acres": round(total_land, 1),
        "total_sales": round(total_sales, 2),
        "avg_income": round(total_income / len(farmers)),
        "total_transactions": len(transactions),
        "crops_cultivated": len(crops_data),
        "villages_covered": len(set(f["village"] for f in farmers)),
    }

# (rest of your code remains unchanged...)