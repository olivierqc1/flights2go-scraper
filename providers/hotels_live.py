# API Hotel Search signée de Travelpayouts (vrais hôtels, vraies notes).
# Flux en 2 temps : start.json lance la recherche, results.json récupère.
# Signature = md5("token:marker:val1:val2:...") avec les valeurs triées
# par ordre alphabétique des noms de paramètres.
# Env vars : TP_TOKEN, TP_MARKER

import os
import hashlib
import asyncio
import httpx

TP_TOKEN = os.getenv("TP_TOKEN", "")
TP_MARKER = os.getenv("TP_MARKER", "")

START_URL = "https://engine.hotellook.com/api/v2/search/start.json"
RESULTS_URL = "https://engine.hotellook.com/api/v2/search/getResult.json"

def _sign(params: dict) -> str:
    values = [str(params[k]) for k in sorted(params.keys())]
    raw = ":".join([TP_TOKEN, TP_MARKER] + values)
    return hashlib.md5(raw.encode()).hexdigest()

async def search_hotels_live(iata: str, checkin: str, checkout: str,
                             adults: int = 2, lang: str = "en",
                             customer_ip: str = "127.0.0.1"):
    """Retourne la liste brute d'hôtels de l'API, ou None si échec."""
    params = {
        "iata": iata,
        "checkIn": checkin,
        "checkOut": checkout,
        "adultsCount": adults,
        "childrenCount": 0,
        "currency": "eur",
        "lang": lang,
        "customerIP": customer_ip,
        "waitForResult": 0,
    }
    params["marker"] = TP_MARKER
    sig_params = {k: v for k, v in params.items() if k != "marker"}
    params["signature"] = _sign(sig_params)

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(START_URL, params=params)
            r.raise_for_status()
            data = r.json()
            search_id = data.get("searchId")
            if not search_id:
                print(f"hotels_live start failed: {data}")
                return None

            res_sig = hashlib.md5(
                f"{TP_TOKEN}:{TP_MARKER}:{search_id}".encode()
            ).hexdigest()

            for _ in range(6):  # ~12s max
                await asyncio.sleep(2)
                r2 = await client.get(RESULTS_URL, params={
                    "searchId": search_id,
                    "marker": TP_MARKER,
                    "signature": res_sig,
                    "limit": 30,
                    "sortBy": "price",
                    "sortAsc": 1,
                })
                if r2.status_code != 200:
                    continue
                body = r2.json()
                if isinstance(body, dict) and body.get("status") == "ok":
                    continue  # encore en cours
                result = body.get("result") if isinstance(body, dict) else body
                if result:
                    return result
            return []
    except Exception as e:
        print(f"hotels_live error {iata}: {e}")
        return None