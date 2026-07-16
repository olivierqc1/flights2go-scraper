# Hôtels : deeplinks Hotellook pré-remplis + estimation de prix.
# Env var : TP_MARKER

import os
from urllib.parse import quote

TP_MARKER = os.getenv("TP_MARKER", "")

HOTEL_LABELS = {
    "fr": "Hôtels disponibles",
    "en": "Hotels available",
    "es": "Hoteles disponibles",
}

MIN_PER_NIGHT = 25  # seuil minimal réaliste en Europe

def build_hotel_option(city_en: str, checkin: str, checkout: str,
                       nights: int, budget_remaining: float,
                       lang: str = "en"):
    """Option hôtel : estimation (60% du budget/nuit dispo) + deeplink.
    Retourne None si le budget par nuit est trop bas."""
    per_night_budget = budget_remaining / max(nights, 1)
    if per_night_budget < MIN_PER_NIGHT:
        return None
    est_per_night = round(per_night_budget * 0.6)
    url = (
        "https://search.hotellook.com/hotels"
        f"?destination={quote(city_en)}"
        f"&checkIn={checkin}&checkOut={checkout}"
        f"&adults=2&currency=eur&language={lang}"
        f"&marker={TP_MARKER}"
    )
    return {
        "name": HOTEL_LABELS.get(lang, HOTEL_LABELS["en"]),
        "price_per_night": float(est_per_night),
        "total_price": round(est_per_night * nights, 2),
        "rating": 0,
        "booking_url": url,
    }