# Hébergement : estimation selon le type + deeplink Hotellook.
# Env var : TP_MARKER

import os
from urllib.parse import quote

TP_MARKER = os.getenv("TP_MARKER", "")

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
                       lang: str = "en", accommodation: str = "hotel",
                       travelers: int = 1):
    """Estimation pour le groupe entier (chambres doubles) + deeplink."""
    acc = accommodation if accommodation in FACTORS else "hotel"
    rooms = max(1, (travelers + 1) // 2)  # 2 personnes par chambre
    per_room_night_budget = budget_remaining / max(nights, 1) / rooms
    if per_room_night_budget < MIN_PER_NIGHT[acc]:
        return None
    est_room_night = round(per_room_night_budget * FACTORS[acc])
    labels = LABELS[acc]
    url = (
        "https://search.hotellook.com/hotels"
        f"?destination={quote(city_en)}"
        f"&checkIn={checkin}&checkOut={checkout}"
        f"&adults={travelers}&currency=eur&language={lang}"
        f"&marker={TP_MARKER}"
    )
    return {
        "name": labels.get(lang, labels["en"]),
        "price_per_night": float(est_room_night * rooms),  # groupe/nuit
        "total_price": round(est_room_night * rooms * nights, 2),
        "rating": 0,
        "booking_url": url,
    }