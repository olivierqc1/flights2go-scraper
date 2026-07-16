# Hôtels via Hotellook (Travelpayouts) — endpoint cache public.
# Env var : TP_MARKER (pour les liens affiliés)

import os
import httpx

TP_MARKER = os.getenv("TP_MARKER", "")
API_URL = "https://engine.hotellook.com/api/v2/cache.json"

async def fetch_hotels(client: httpx.AsyncClient, city_en: str,
                       checkin: str, checkout: str, nights: int,
                       max_per_night: float, min_rating: int):
    """Hôtels les moins chers dans une ville (nom anglais requis)."""
    params = {
        "location": city_en,
        "checkIn": checkin,
        "checkOut": checkout,
        "currency": "eur",
        "limit": 15,
    }
    try:
        r = await client.get(API_URL, params=params, timeout=15)
        r.raise_for_status()
        hotels = r.json()
        results = []
        for h in hotels:
            total = float(h.get("priceFrom", 0))
            if total <= 0:
                continue
            per_night = total / max(nights, 1)
            stars = int(h.get("stars", 0) or 0)
            if per_night > max_per_night:
                continue
            if min_rating and stars < min_rating:
                continue
            results.append({
                "name": h.get("hotelName", "Hotel"),
                "price_per_night": round(per_night, 2),
                "total_price": round(total, 2),
                "rating": stars,
                "booking_url": (
                    "https://search.hotellook.com/hotels"
                    f"?destination={city_en}&checkIn={checkin}"
                    f"&checkOut={checkout}&marker={TP_MARKER}"
                ),
            })
        results.sort(key=lambda x: x["total_price"])
        return results
    except Exception as e:
        print(f"hotel error {city_en}: {e}")
        return []