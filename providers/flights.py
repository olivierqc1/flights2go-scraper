# Vols via Travelpayouts Data API (Aviasales) — remplace le scraper.
# Env vars requis : TP_TOKEN, TP_MARKER

import os
import httpx

TP_TOKEN = os.getenv("TP_TOKEN", "")
TP_MARKER = os.getenv("TP_MARKER", "")

API_URL = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"

async def fetch_flight(client: httpx.AsyncClient, origin: str, dest: str, month: str):
    """Meilleur prix vol origin->dest pour un mois donné (YYYY-MM)."""
    params = {
        "origin": origin,
        "destination": dest,
        "departure_at": month,
        "currency": "eur",
        "sorting": "price",
        "limit": 1,
        "one_way": "false",
        "token": TP_TOKEN,
    }
    try:
        r = await client.get(API_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json().get("data", [])
        if not data:
            return None
        f = data[0]
        link = f.get("link", "")
        return {
            "mode": "flight",
            "price": float(f.get("price", 0)),
            "duration_hours": round(f.get("duration", 0) / 60, 1) if f.get("duration") else None,
            "stops": f.get("transfers", 0),
            "carrier": f.get("airline"),
            "booking_url": f"https://www.aviasales.com{link}&marker={TP_MARKER}",
        }
    except Exception as e:
        print(f"flight error {origin}->{dest}: {e}")
        return None