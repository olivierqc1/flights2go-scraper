# Endpoint /hotels/{code} : vrais hôtels pour une destination,
# avec filtres note / distance / prix max par nuit.

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional

from data.destinations import DESTINATIONS
from providers.hotels_live import search_hotels_live, TP_MARKER

router = APIRouter()

class LiveHotel(BaseModel):
    name: str
    stars: int
    guest_score: Optional[float] = None   # sur 10
    price_per_night: float
    total_price: float
    distance_km: Optional[float] = None   # du centre
    booking_url: str

@router.get("/hotels/{code}", response_model=List[LiveHotel])
async def hotels_for_destination(
    code: str,
    request: Request,
    checkin: str,
    checkout: str,
    adults: int = 2,
    nights: int = 1,
    lang: str = "en",
    min_score: float = 0,      # ex. 8 pour "note 8+"
    max_distance: float = -1,  # km du centre, -1 = peu importe
    max_per_night: float = -1, # -1 = peu importe
):
    code = code.upper()
    if code not in DESTINATIONS:
        raise HTTPException(404, f"Destination inconnue: {code}")

    ip = request.client.host if request.client else "127.0.0.1"
    raw = await search_hotels_live(code, checkin, checkout, adults, lang, ip)
    if raw is None:
        raise HTTPException(502, "hotel search unavailable")

    out = []
    for h in raw:
        total = float(h.get("minPriceTotal") or h.get("price") or 0)
        if total <= 0:
            continue
        per_night = total / max(nights, 1)
        score = h.get("guestScore")
        score10 = round(float(score) / 10, 1) if score else None
        dist = h.get("distance")
        if min_score and (score10 is None or score10 < min_score):
            continue
        if max_distance != -1 and dist is not None and float(dist) > max_distance:
            continue
        if max_per_night != -1 and per_night > max_per_night:
            continue
        hotel_id = h.get("id", "")
        url = (
            "https://search.hotellook.com/hotels"
            f"?hotelId={hotel_id}&checkIn={checkin}&checkOut={checkout}"
            f"&adults={adults}&currency=eur&language={lang}"
            f"&marker={TP_MARKER}"
        )
        out.append(LiveHotel(
            name=h.get("name") or h.get("hotelName") or "Hotel",
            stars=int(h.get("stars", 0) or 0),
            guest_score=score10,
            price_per_night=round(per_night, 2),
            total_price=round(total, 2),
            distance_km=round(float(dist), 1) if dist is not None else None,
            booking_url=url,
        ))

    out.sort(key=lambda x: x.price_per_night)
    return out[:15]