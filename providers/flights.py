# Vols via Travelpayouts Data API (Aviasales).
# Demande 10 options et choisit la moins chère "raisonnable"
# (durée et escales plafonnées) pour éviter les itinéraires absurdes.
# Env vars requis : TP_TOKEN, TP_MARKER

import os
import httpx

TP_TOKEN = os.getenv("TP_TOKEN", "")
TP_MARKER = os.getenv("TP_MARKER", "")

API_URL = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"

MAX_DURATION_HOURS = 12   # intra-Europe : au-delà, c'est du junk
MAX_TRANSFERS = 1

async def fetch_flight(client: httpx.AsyncClient, origin: str, dest: str, month: str):
    """Meilleur vol raisonnable origin->dest pour un mois donné (YYYY-MM)."""
    params = {
        "origin": origin,
        "destination": dest,
        "departure_at": month,
        "currency": "eur",
        "sorting": "price",
        "limit": 10,
        "one_way": "false",
        "token": TP_TOKEN,
    }
    try:
        r = await client.get(API_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json().get("data", [])
        best = None
        for f in data:
            duration_h = (f.get("duration") or 0) / 60
            transfers = f.get("transfers", 0)
            if duration_h and duration_h > MAX_DURATION_HOURS:
                continue
            if transfers > MAX_TRANSFERS:
                continue
            price = float(f.get("price", 0))
            if price <= 0:
                continue
            if best is None or price < best["price"]:
                link = f.get("link", "")
                best = {
                    "mode": "flight",
                    "price": price,
                    "duration_hours": round(duration_h, 1) if duration_h else None,
                    "stops": transfers,
                    "carrier": f.get("airline"),
                    "booking_url": f"https://www.aviasales.com{link}&marker={TP_MARKER}",
                }
        return best
    except Exception as e:
        print(f"flight error {origin}->{dest}: {e}")
        return None