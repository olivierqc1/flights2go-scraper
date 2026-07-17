from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import asyncio
from datetime import date, timedelta
import httpx

from data.destinations import DESTINATIONS, localize
from providers.flights import fetch_flight
from providers.hotels import build_hotel_option
from providers.ground import get_ground_transport
from providers.currency import get_rates, normalize
from routes_hotels import router as hotels_router

app = FastAPI(title="Travel2Go API - Europe", version="4.6.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(hotels_router)

BAG_FEE_PER_TRIP = 30.0

class SearchFilters(BaseModel):
    transportModes: List[str] = ["flight", "train", "bus"]
    maxStops: int = -1
    maxTravelHours: int = -1
    bags: int = 0
    accommodationType: str = "hotel"
    excludeCountries: List[str] = []
    minHotelRating: int = 0

class SearchRequest(BaseModel):
    origin: str
    budget: float               # dans la devise choisie
    currency: str = "EUR"
    month: str
    nights: int = 5
    travelers: int = 1
    tripType: str = "month"     # month | weekend
    lang: str = "fr"
    filters: SearchFilters = Field(default_factory=SearchFilters)

class TransportInfo(BaseModel):
    mode: str
    price: float
    duration_hours: Optional[float] = None
    stops: Optional[int] = 0
    carrier: Optional[str] = None
    departure_date: Optional[str] = None
    booking_url: str

class HotelInfo(BaseModel):
    name: str
    price_per_night: float
    total_price: float
    rating: float
    booking_url: str
    alt_booking_url: Optional[str] = None

class TravelPackage(BaseModel):
    destination: str
    country: str
    code: str
    flag: str
    currency: str
    transport: TransportInfo
    hotel: HotelInfo
    total_cost: float
    budget_remaining: float
    savings_pct: float

def default_checkin(month: str) -> str:
    try:
        y, m = (int(x) for x in month.split("-"))
        return date(y, m, 10).isoformat()
    except Exception:
        raise HTTPException(400, "month doit être au format YYYY-MM")

def stay_dates(checkin_str: str, nights: int):
    d0 = date.fromisoformat(checkin_str)
    return checkin_str, (d0 + timedelta(days=max(nights, 1))).isoformat()

def is_excluded(code: str, excluded: List[str]) -> bool:
    if not excluded:
        return False
    names = set(n.lower() for n in DESTINATIONS[code]["country"].values())
    return any(e.lower() in names for e in excluded)

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

@app.post("/search/packages", response_model=List[TravelPackage])
async def search_packages(req: SearchRequest):
    origin = req.origin.upper()
    if origin not in DESTINATIONS:
        raise HTTPException(400, f"Origine inconnue: {origin}")

    f = req.filters
    modes = f.transportModes
    bags = max(0, min(f.bags, 2))
    trav = max(1, min(req.travelers, 8))
    weekend = req.tripType == "weekend"
    nights = min(req.nights, 3) if weekend else req.nights

    cur = normalize(req.currency)
    rates = await get_rates()
    rate = rates.get(cur, 1.0)
    budget_eur = req.budget / rate if rate else req.budget

    max_transport_budget = budget_eur * 0.5
    base_checkin = default_checkin(req.month)

    dests = [
        c for c in DESTINATIONS
        if c != origin and not is_excluded(c, f.excludeCountries)
    ]

    async with httpx.AsyncClient() as client:
        flight_results = {}
        if "flight" in modes:
            tasks = [
                fetch_flight(client, origin, d, req.month, weekend)
                for d in dests
            ]
            for d, res in zip(dests, await asyncio.gather(*tasks)):
                flight_results[d] = res

    transport_by_dest = {}
    for d in dests:
        options = []
        fl = flight_results.get(d)
        if fl:
            fl = dict(fl)
            fl["price"] = (fl["price"] + bags * BAG_FEE_PER_TRIP * 2) * trav
            options.append(fl)
        for g in get_ground_transport(origin, d, modes, f.maxTravelHours):
            g = dict(g)
            g["price"] = g["price"] * trav
            options.append(g)
        best = pick_best_transport(options, f.maxStops, f.maxTravelHours)
        if best and best["price"] <= max_transport_budget:
            transport_by_dest[d] = best

    cv = lambda x: round(x * rate, 2)  # EUR -> devise choisie

    packages = []
    for d, t in transport_by_dest.items():
        checkin, checkout = stay_dates(
            t.get("departure_date") or base_checkin, nights
        )
        remaining = budget_eur - t["price"]
        hotel = build_hotel_option(
            DESTINATIONS[d]["names"]["en"],
            checkin, checkout, nights, remaining,
            req.lang, f.accommodationType, trav,
        )
        if hotel is None:
            continue
        total = t["price"] + hotel["total_price"]
        left = budget_eur - total
        if left < 0:
            continue
        loc = localize(d, req.lang)
        t_out = dict(t)
        t_out["price"] = cv(t["price"])
        h_out = dict(hotel)
        h_out["price_per_night"] = cv(hotel["price_per_night"])
        h_out["total_price"] = cv(hotel["total_price"])
        packages.append(TravelPackage(
            destination=loc["name"],
            country=loc["country"],
            code=d,
            flag=loc["flag"],
            currency=cur,
            transport=TransportInfo(**t_out),
            hotel=HotelInfo(**h_out),
            total_cost=cv(total),
            budget_remaining=cv(left),
            savings_pct=round(left / budget_eur * 100, 1),
        ))

    packages.sort(key=lambda p: -p.budget_remaining)
    return packages

@app.get("/destinations")
async def list_destinations(lang: str = "fr"):
    return [localize(c, lang) for c in DESTINATIONS]

@app.get("/")
async def root():
    return {"service": "Travel2Go API - Europe", "version": "4.6.0"}