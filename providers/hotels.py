# Hôtels : deeplinks Hotellook pré-remplis + budget par nuit calculé.
# Plus d'appel API (l'endpoint cache.json de Hotellook est mort) —
# la commission se fait via le deeplink avec le marker.
# Env var : TP_MARKER

import os
from urllib.parse import quote

TP_MARKER = os.getenv("TP_MARKER", "")

HOTEL_LABELS = {
    "fr": "Hôtels dès ~{price}€/nuit",
    "en": "Hotels from ~{price}€/night",
    "es": "Hoteles desde ~{price}€/noche",
}

def build_hotel_option(city_en: str, checkin: str, checkout: str,
                       nights: int, budget_remaining: float,
                       lang: str = "en"):
    """Construit l'option hôtel basée sur le budget restant.
    Retourne None si le budget par nuit est trop bas pour être réaliste."""
    per_night = budget_remaining / max(nights, 1)
    if per_night < 25:  # seuil minimal réaliste en Europe
        return None
    # Estimation affichée : ~60% du budget/nuit = fourchette basse crédible
    est_from = round(per_night * 0.6)
    label_tpl = HOTEL_LABELS.get(lang, HOTEL_LABELS["en"])
    url = (
        "https://search.hotellook.com/hotels"
        f"?destination={quote(city_en)}"
        f"&checkIn={checkin}&checkOut={checkout}"
        f"&adults=2&currency=eur&language={lang}"
        f"&marker={TP_MARKER}"
    )
    return {
        "name": label_tpl.format(price=est_from),
        "price_per_night": round(per_night, 2),
        "total_price": round(budget_remaining, 2),
        "rating": 0,
        "booking_url": url,
    }