# Hébergement : estimation selon le type + deeplink Hotellook.
# Env var : TP_MARKER

import os
from urllib.parse import quote

TP_MARKER = os.getenv("TP_MARKER", "")

# Facteur d'estimation du prix/nuit selon le type (part du budget/nuit dispo)
FACTORS = {"hotel": 0.6, "hostel": 0.35, "any": 0.5}
MIN_PER_NIGHT = {"hotel": 25, "hostel": 15, "any": 20}

LABELS = {
    "hotel": {"fr": "Hôtels disponibles", "en": "Hotels available",
              "es": "Hoteles disponibles"},
    "hostel": {"fr": "Auberges de jeunesse", "en": "Hostels",
               "es": "Albergues juveniles"},
    "any": {"fr": "Hébergements disponibles", "en": "Places to stay",
            "es": "Alojamientos disponibles"},
}

def build_hotel_option(city_en: str, checkin: str, checkout: str,
                       nights: int, budget_remaining: float,
                       lang: str = "en", accommodation: str = "hotel"):
    acc = accommodation if accommodation in FACTORS else "hotel"
    per_night_budget = budget_remaining / max(nights, 1)
    if per_night_budget < MIN_PER_NIGHT[acc]:
        return None
    est_per_night = round(per_night_budget * FACTORS[acc])
    labels = LABELS[acc]
    url = (
        "https://search.hotellook.com/hotels"
        f"?destination={quote(city_en)}"
        f"&checkIn={checkin}&checkOut={checkout}"
        f"&adults=2&currency=eur&language={lang}"
        f"&marker={TP_MARKER}"
    )
    return {
        "name": labels.get(lang, labels["en"]),
        "price_per_night": float(est_per_night),
        "total_price": round(est_per_night * nights, 2),
        "rating": 0,
        "booking_url": url,
    }