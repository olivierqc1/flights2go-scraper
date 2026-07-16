# Vols Aviasales : jusqu'à 30 options, filtre les itinéraires absurdes,
# mode week-end (départs jeu/ven/sam), retourne la date de départ.
# Env vars : TP_TOKEN, TP_MARKER

import os
from datetime import date
import httpx

TP_TOKEN = os.getenv("TP_TOKEN", "")
TP_MARKER = os.getenv("TP_MARKER", "")

API_URL = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"

MAX_DURATION_HOURS = 12
MAX_TRANSFERS = 1
WEEKEND_DAYS = (3, 4, 5)  # jeu, ven, sam (lundi=0)

async def fetch_flight(client: httpx.AsyncClient, origin: str, dest: str,
                       month: str, weekend: bool = False):
    params = {
        "origin": origin,
        "destination": dest,
        "departure_at": month,
        "currency": "eur",
        "sorting": "price",
        "limit": 30,
        "one_way": "false",
        "token": TP_TOKEN,
    }
    try:
        r = await client.get(API_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json().get("data", [])
        best = None
        for f in data:
            dep_raw = (f.get("departure_at") or "")[:10]
            if weekend and dep_raw:
                try:
                    if date.fromisoformat(dep_raw).weekday() not in WEEKEND_DAYS:
                        continue
                except ValueError:
                    continue
            duration_h = (f.get("duration") or 0) / 60
            if duration_h and duration_h > MAX_DURATION_HOURS:
                continue
            if f.get("transfers", 0) > MAX_TRANSFERS:
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
                    "stops": f.get("transfers", 0),
                    "carrier": f.get("airline"),
                    "departure_date": dep_raw or None,
                    "booking_url": f"https://www.aviasales.com{link}&marker={TP_MARKER}",
                }
        return best
    except Exception as e:
        print(f"flight error {origin}->{dest}: {e}")
        return None