# Train / bus — dataset curé + deeplinks Omio.
# Env var optionnel : OMIO_PREFIX (wrapper affilié fourni par ton
# réseau d'affiliation ; si vide, lien Omio direct).

import os
from data.ground_routes import get_ground_options
from data.destinations import DESTINATIONS

OMIO_PREFIX = os.getenv("OMIO_PREFIX", "")

def omio_link(origin: str, dest: str) -> str:
    o = DESTINATIONS[origin]["slug"]
    d = DESTINATIONS[dest]["slug"]
    url = f"https://www.omio.com/travel/{o}/{d}"
    return f"{OMIO_PREFIX}{url}" if OMIO_PREFIX else url

def get_ground_transport(origin: str, dest: str, allowed_modes: list,
                         max_hours: int = -1):
    """Options train/bus filtrées, format identique aux vols."""
    options = []
    for opt in get_ground_options(origin, dest):
        if opt["mode"] not in allowed_modes:
            continue
        if max_hours != -1 and opt["hours"] > max_hours:
            continue
        options.append({
            "mode": opt["mode"],
            "price": float(opt["price_from"]),
            "duration_hours": opt["hours"],
            "stops": 0,
            "carrier": opt["carrier"],
            "booking_url": omio_link(origin, dest),
        })
    return options