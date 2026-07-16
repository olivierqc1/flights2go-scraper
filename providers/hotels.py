# Hébergement : estimation + deeplink Hotellook, et Hostelworld en plus
# pour les auberges (alt_booking_url).
# Env vars : TP_MARKER, HW_PREFIX (optionnel, wrapper affilié Hostelworld)

import os
from urllib.parse import quote

TP_MARKER = os.getenv("TP_MARKER", "")
HW_PREFIX = os.getenv("HW_PREFIX", "")

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

def hostelworld_url(city_en: str, checkin: str, checkout: str, guests: int) -> str:
    url = (
        "https://www.hostelworld.com/s"
        f"?q={quote(city_en)}&from={checkin}&to={checkout}&guests={guests}"
    )
    return f"{HW_PREFIX}{url}" if HW_PREFIX else url

def build_hotel_option(city_en: str, checkin: str, checkout: str,
                       nights: int, budget_remaining: float,
                       lang: str = "en", accommodation: str = "hotel",
                       travelers: int = 1):
    acc = accommodation if accommodation in FACTORS else "hotel"
    rooms = max(1, (travelers + 1) // 2)
    per_room_night_budget = budget_remaining / max(nights, 1) / rooms
    if per_room_night_budget < MIN_PER_NIGHT[acc]:
        return None
    est_room_night = round(per_room_night_budget * FACTORS[acc])
    labels = LABELS[acc]
    hotellook = (
        "https://search.hotellook.com/hotels"
        f"?destination={quote(city_en)}"
        f"&checkIn={checkin}&checkOut={checkout}"
        f"&adults={travelers}&currency=eur&language={lang}"
        f"&marker={TP_MARKER}"
    )
    alt = None
    if acc in ("hostel", "any"):
        alt = hostelworld_url(city_en, checkin, checkout, travelers)
    return {
        "name": labels.get(lang, labels["en"]),
        "price_per_night": float(est_room_night * rooms),
        "total_price": round(est_room_night * rooms * nights, 2),
        "rating": 0,
        "booking_url": hotellook,
        "alt_booking_url": alt,
    }