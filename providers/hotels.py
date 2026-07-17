# Hébergement : estimation basée sur le budget + deeplinks.
# Cible Booking.com (accepte ville en texte + dates dans l'URL).
# Wrapper affilié optionnel via env var. Hostelworld pour les auberges.
# Env vars :
#   HOTEL_AFF_PREFIX : wrapper affilié finissant par "&u=" (vide = direct)
#   HW_PREFIX : wrapper affilié Hostelworld (optionnel)

import os
from urllib.parse import quote

from providers.hotel_labels import hotel_label

HOTEL_AFF_PREFIX = os.getenv("HOTEL_AFF_PREFIX", "")
HW_PREFIX = os.getenv("HW_PREFIX", "")

FACTORS = {"hotel": 0.6, "hostel": 0.35, "any": 0.5}
MIN_PER_NIGHT = {"hotel": 25, "hostel": 15, "any": 20}

def booking_url(city_en: str, checkin: str, checkout: str, adults: int) -> str:
    target = (
        "https://www.booking.com/searchresults.html"
        f"?ss={quote(city_en)}"
        f"&checkin={checkin}&checkout={checkout}"
        f"&group_adults={adults}&no_rooms={max(1, (adults + 1) // 2)}"
        f"&group_children=0"
    )
    if HOTEL_AFF_PREFIX:
        return f"{HOTEL_AFF_PREFIX}{quote(target, safe='')}"
    return target

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
    alt = None
    if acc in ("hostel", "any"):
        alt = hostelworld_url(city_en, checkin, checkout, travelers)
    return {
        "name": hotel_label(acc, lang),
        "price_per_night": float(est_room_night * rooms),
        "total_price": round(est_room_night * rooms * nights, 2),
        "rating": 0,
        "booking_url": booking_url(city_en, checkin, checkout, travelers),
        "alt_booking_url": alt,
    }