from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
from datetime import datetime
import os

app = FastAPI(title="Travel2Go API - Complete Search")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MODELS
# ============================================================================

class SearchFilters(BaseModel):
    maxStops: int = -1             # -1 = peu importe, 0 = direct, 1 = 1 escale, 2 = 2 escales
    maxFlightDuration: int = -1    # en heures, -1 = peu importe
    baggageIncluded: bool = False
    minHotelRating: int = 0        # 0 = toutes, 3, 4, 5
    accommodationType: str = "all" # "all", "hotel", "hostel", "apartment"

class SearchRequest(BaseModel):
    origin: str
    budget: float
    period: str
    nights: int = 7
    filters: SearchFilters = SearchFilters()

class FlightInfo(BaseModel):
    price: float
    duration_hours: Optional[float] = None
    stops: int
    airline: Optional[str] = None
    has_baggage: bool
    affiliate_url: str

class HotelInfo(BaseModel):
    name: str
    price_per_night: float
    total_price: float
    rating: float
    accommodation_type: str  # "hotel", "hostel", "apartment"
    affiliate_url: str

class TravelPackage(BaseModel):
    destination: str
    country: str
    code: str
    flag: str
    flight: FlightInfo
    hotel: HotelInfo
    total_cost: float
    budget_remaining: float
    savings_pct: float

# ============================================================================
# DESTINATIONS (toutes)
# ============================================================================

ALL_DESTINATIONS = [
    # Europe
    'BCN', 'LIS', 'MAD', 'FCO', 'CDG', 'LHR', 'DUB', 'AMS', 'BER', 'PRG',
    'ATH', 'VIE', 'BUD', 'WAW', 'CPH', 'OSL', 'STO', 'HEL', 'ZRH', 'MUC',
    'BRU', 'VCE', 'NAP', 'MXP', 'OPO',
    # Amérique
    'MEX', 'BOG', 'LIM', 'GRU', 'EZE', 'SCL', 'PTY', 'CUN', 'GDL', 'MDE',
    # Asie
    'NRT', 'ICN', 'BKK', 'SIN', 'HKG', 'DEL', 'BOM', 'DXB'
]

# ============================================================================
# MAIN SEARCH
# ============================================================================

@app.post("/search/packages", response_model=List[TravelPackage])
async def search_packages(request: SearchRequest):
    """
    Recherche complète avec tous les filtres
    """
    start_time = datetime.now()
    
    print(f"🔍 COMPLETE SEARCH")
    print(f"   Origin: {request.origin}")
    print(f"   Budget: {request.budget} CAD")
    print(f"   Period: {request.period}")
    print(f"   Nights: {request.nights}")
    print(f"   Filters:")
    print(f"     - Max stops: {request.filters.maxStops}")
    print(f"     - Max duration: {request.filters.maxFlightDuration}h")
    print(f"     - Baggage: {request.filters.baggageIncluded}")
    print(f"     - Min hotel rating: {request.filters.minHotelRating}★")
    print(f"     - Accommodation: {request.filters.accommodationType}")
    
    try:
        from scrapers.flights_multi import scrape_flights_multi
        from scrapers.hotels_booking import scrape_hotels_booking
        
        # 1. Scraper les vols avec filtres
        max_flight_budget = request.budget * 0.5  # 50% du budget pour le vol
        
        flights = await scrape_flights_multi(
            origin=request.origin,
            max_budget=max_flight_budget,
            period=request.period,
            destinations=ALL_DESTINATIONS,
            max_stops=request.filters.maxStops,
            max_duration=request.filters.maxFlightDuration,
            baggage_included=request.filters.baggageIncluded
        )
        
        print(f"✅ Found {len(flights)} matching flights")
        
        if not flights:
            return []
        
        # 2. Pour chaque vol, chercher des hôtels avec filtres
        packages = []
        
        for flight in flights[:20]:  # Limiter à 20 vols pour éviter timeout
            try:
                remaining_budget = request.budget - flight["price"]
                max_hotel_per_night = remaining_budget / request.nights
                
                hotels = await scrape_hotels_booking(
                    city_code=flight["code"],
                    max_price_per_night=max_hotel_per_night,
                    nights=request.nights,
                    period=request.period,
                    min_rating=request.filters.minHotelRating,
                    accommodation_type=request.filters.accommodationType
                )
                
                if not hotels:
                    continue
                
                # Prendre le meilleur hôtel (meilleur rapport qualité/prix)
                best_hotel = hotels[0]
                
                total_hotel_cost = best_hotel["price_per_night"] * request.nights
                total_package_cost = flight["price"] + total_hotel_cost
                budget_remaining = request.budget - total_package_cost
                savings_pct = (budget_remaining / request.budget) * 100
                
                package = TravelPackage(
                    destination=flight["city"],
                    country=flight["country"],
                    code=flight["code"],
                    flag=flight["flag"],
                    flight=FlightInfo(
                        price=flight["price"],
                        duration_hours=flight.get("duration_hours"),
                        stops=flight["stops"],
                        airline=flight.get("airline"),
                        has_baggage=flight["has_baggage"],
                        affiliate_url=flight["affiliate_url"]
                    ),
                    hotel=HotelInfo(
                        name=best_hotel["name"],
                        price_per_night=best_hotel["price_per_night"],
                        total_price=total_hotel_cost,
                        rating=best_hotel["rating"],
                        accommodation_type=best_hotel["accommodation_type"],
                        affiliate_url=best_hotel["affiliate_url"]
                    ),
                    total_cost=total_package_cost,
                    budget_remaining=budget_remaining,
                    savings_pct=savings_pct
                )
                
                packages.append(package)
                
            except Exception as e:
                print(f"Error processing {flight['code']}: {e}")
                continue
        
        # Trier par budget restant (le plus économique en premier)
        packages.sort(key=lambda x: x.budget_remaining, reverse=True)
        
        search_time = (datetime.now() - start_time).total_seconds()
        print(f"✅ Found {len(packages)} complete packages in {search_time:.1f}s")
        
        return packages
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {
        "service": "Travel2Go API",
        "version": "3.0.0",
        "mode": "complete_search_with_filters",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)