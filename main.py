from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import asyncio
import calendar
from datetime import date
import httpx

from data.destinations import DESTINATIONS, localize
from providers.flights import fetch_flight
from providers.hotels import build_hotel_option
from providers.ground import get_ground_transport

app = FastAPI(title="Travel2Go API - Europe", version="4.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# MODELS
# ============================================================

class SearchFilters(BaseModel):
    transportModes: List[str] = ["flight", "train", "bus"]
    maxStops: int = -1          # vols : -1 = peu importe
    maxTravelHours: int = -1    # tous modes : -1 = peu importe
    minHotelRating: int = 0     # conservé pour compat, non utilisé

class SearchRequest(BaseModel):
    origin: str                 # code ville IATA, ex. "BCN"
    budget: float               # budget total EUR
    month: str                  # "YYYY-MM"
    nights: int = 5
    lang: str = "fr"            # fr | en | es
    filters: SearchFilters = Field(default_factory=SearchFilters)

class TransportInfo(BaseModel):
    mode: str
    price: float
    duration_hours: Optional[float] = None
    stops: Optional[int] = 0
    carrier: Optional[str] = None
    booking_url: str

class HotelInfo(BaseModel):
    name: str
    price_per_night: float
    total_price: float
    rating: float
    booking_url: str

class TravelPackage(BaseModel):
    destination: str
    country: str
    code: str
    flag: str
    transport: TransportInfo
    hotel: HotelInfo
    total_cost: float
    budget_remaining: float
    savings_pct: float

# ============================================================
# HELPERS
# ============================================================

def dates_from_month(month: str, nights: int):
    """'2026-09' -> (check-in le 10, check-out 10+nights)."""
    try:
        y, m = (int(x) for x in month.split("-"))
        start = date(y, m, 10)
        last_day = calendar.monthrange(y, m)[1]
        end_day = min(10 + nights, last_day)
        end = date(y, m, end_day)
        return start.isoformat(), end.isoformat()
    except Exception:
        raise HTTPException(400, "month doit être au format YYYY-MM")

def pick_best_transport(options: list, max_stops: int, max_hours: int):
    valid = []
    for o in options:
        if o is None:
            continue
        if o["mode"] == "flight":
            if max_stops != -1 and (o.get("stops") or 0) > max_stops:
                continue
            if max_hours != -1 and o.get("duration_hours") \
               and o["duration_hours"] > max_hours:
                continue
        valid.append(o)
    return min(valid, key=lambda x: x["price"]) if valid else None

# ============================================================
# SEARCH
# ============================================================

@app.post("/search/packages", response_model=List[TravelPackage])
async def search_packages(req: SearchRequest):
    origin = req.origin.upper()
    if origin not in DESTINATIONS:
        raise HTTPException(400, f"Origine inconnue: {origin}")

    modes = req.filters.transportModes
    max_transport_budget = req.budget * 0.5
    checkin, checkout = dates_from_month(req.month, req.nights)
    dests = [c for c in DESTINATIONS if c != origin]

    async with httpx.AsyncClient() as client:
        # 1. Vols (concurrent) si mode activé
        flight_results = {}
        if "flight" in modes:
            tasks = [fetch_flight(client, origin, d, req.month) for d in dests]
            for d, res in zip(dests, await asyncio.gather(*tasks)):
                flight_results[d] = res

    # 2. Meilleur transport par destination (vol vs train vs bus)
    transport_by_dest = {}
    for d in dests:
        options = []
        if flight_results.get(d):
            options.append(flight_results[d])
        options += get_ground_transport(
            origin, d, modes, req.filters.maxTravelHours
        )
        best = pick_best_transport(
            options, req.filters.maxStops, req.filters.maxTravelHours
        )
        if best and best["price"] <= max_transport_budget:
            transport_by_dest[d] = best

    # 3. Assembler les packages avec budget hôtel + deeplink
    packages = []
    for d, t in transport_by_dest.items():
        remaining = req.budget - t["price"]
        hotel = build_hotel_option(
            DESTINATIONS[d]["names"]["en"],
            checkin, checkout, req.nights, remaining, req.lang,
        )
        if hotel is None:
            continue  # budget/nuit trop bas pour être réaliste
        total = t["price"] + hotel["total_price"]
        loc = localize(d, req.lang)
        packages.append(TravelPackage(
            destination=loc["name"],
            country=loc["country"],
            code=d,
            flag=loc["flag"],
            transport=TransportInfo(**t),
            hotel=HotelInfo(**hotel),
            total_cost=round(total, 2),
            budget_remaining=round(req.budget - total, 2),
            savings_pct=0.0,
        ))

    # Trier : transport le moins cher d'abord = plus de budget hôtel
    packages.sort(key=lambda p: p.transport.price)
    return packages

@app.get("/destinations")
async def list_destinations(lang: str = "fr"):
    return [localize(c, lang) for c in DESTINATIONS]

@app.get("/")
async def root():
    return {
        "service": "Travel2Go API - Europe",
        "version": "4.1.0",
        "langs": ["fr", "en", "es"],
        "transport_modes": ["flight", "train", "bus"],
    }