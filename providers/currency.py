# Taux de change BCE via frankfurter.app (gratuit, sans clé).
# Cache en mémoire 12h. Tout est calculé en EUR puis converti.

import time
import httpx

SUPPORTED = ("EUR", "USD", "CAD", "GBP", "CHF", "PLN", "SEK", "CZK", "DKK")

_cache = {"rates": {"EUR": 1.0}, "ts": 0.0}
TTL = 12 * 3600

async def get_rates() -> dict:
    now = time.time()
    if now - _cache["ts"] < TTL and len(_cache["rates"]) > 1:
        return _cache["rates"]
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                "https://api.frankfurter.app/latest",
                params={"from": "EUR", "to": ",".join(c for c in SUPPORTED if c != "EUR")},
                timeout=10,
            )
            r.raise_for_status()
            rates = r.json().get("rates", {})
            rates["EUR"] = 1.0
            _cache["rates"] = rates
            _cache["ts"] = now
    except Exception as e:
        print(f"currency error: {e}")
    return _cache["rates"]

def normalize(cur: str) -> str:
    cur = (cur or "EUR").upper()
    return cur if cur in SUPPORTED else "EUR"