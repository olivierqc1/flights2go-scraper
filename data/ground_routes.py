# Routes train/bus curées (prix typiques min. en EUR, durées en heures).
# Pas d'API publique de recherche chez Omio → on utilise un dataset
# maintenu à la main + deeplinks Omio. Facile à étendre.

# Format : (origin, dest): [ {mode, hours, price_from, carrier}, ... ]

GROUND_ROUTES = {
    # --- Depuis Barcelone ---
    ("BCN", "MAD"): [
        {"mode": "train", "hours": 2.7, "price_from": 35, "carrier": "AVE/Ouigo/Iryo"},
        {"mode": "bus", "hours": 7.5, "price_from": 25, "carrier": "ALSA/FlixBus"},
    ],
    ("BCN", "VLC"): [
        {"mode": "train", "hours": 2.9, "price_from": 20, "carrier": "Euromed"},
        {"mode": "bus", "hours": 4.3, "price_from": 17, "carrier": "ALSA"},
    ],
    ("BCN", "SVQ"): [
        {"mode": "train", "hours": 5.7, "price_from": 55, "carrier": "AVE"},
    ],
    ("BCN", "PAR"): [
        {"mode": "train", "hours": 6.8, "price_from": 59, "carrier": "TGV/Renfe"},
        {"mode": "bus", "hours": 14.5, "price_from": 40, "carrier": "FlixBus/BlaBlaCar"},
    ],
    ("BCN", "LYS"): [
        {"mode": "train", "hours": 5.0, "price_from": 49, "carrier": "TGV/Renfe"},
        {"mode": "bus", "hours": 9.0, "price_from": 33, "carrier": "FlixBus"},
    ],
    ("BCN", "MRS"): [
        {"mode": "train", "hours": 4.5, "price_from": 45, "carrier": "TGV/Renfe"},
        {"mode": "bus", "hours": 7.5, "price_from": 30, "carrier": "FlixBus"},
    ],
    ("BCN", "NCE"): [
        {"mode": "bus", "hours": 10.0, "price_from": 40, "carrier": "FlixBus"},
    ],
    # --- Depuis Madrid ---
    ("MAD", "BCN"): [
        {"mode": "train", "hours": 2.7, "price_from": 35, "carrier": "AVE/Ouigo/Iryo"},
        {"mode": "bus", "hours": 7.5, "price_from": 25, "carrier": "ALSA/FlixBus"},
    ],
    ("MAD", "VLC"): [
        {"mode": "train", "hours": 1.8, "price_from": 22, "carrier": "AVE/Ouigo/Iryo"},
        {"mode": "bus", "hours": 4.2, "price_from": 18, "carrier": "ALSA"},
    ],
    ("MAD", "SVQ"): [
        {"mode": "train", "hours": 2.7, "price_from": 30, "carrier": "AVE/Ouigo/Iryo"},
        {"mode": "bus", "hours": 6.3, "price_from": 22, "carrier": "ALSA"},
    ],
    ("MAD", "LIS"): [
        {"mode": "bus", "hours": 8.0, "price_from": 38, "carrier": "ALSA/FlixBus"},
    ],
    ("MAD", "OPO"): [
        {"mode": "bus", "hours": 8.5, "price_from": 40, "carrier": "ALSA"},
    ],
    # --- Depuis Paris ---
    ("PAR", "LON"): [
        {"mode": "train", "hours": 2.3, "price_from": 52, "carrier": "Eurostar"},
        {"mode": "bus", "hours": 8.5, "price_from": 30, "carrier": "FlixBus"},
    ],
    ("PAR", "BRU"): [
        {"mode": "train", "hours": 1.4, "price_from": 29, "carrier": "Eurostar/TGV"},
        {"mode": "bus", "hours": 4.0, "price_from": 15, "carrier": "FlixBus/BlaBlaCar"},
    ],
    ("PAR", "AMS"): [
        {"mode": "train", "hours": 3.3, "price_from": 39, "carrier": "Eurostar"},
        {"mode": "bus", "hours": 7.0, "price_from": 25, "carrier": "FlixBus"},
    ],
    ("PAR", "LYS"): [
        {"mode": "train", "hours": 2.0, "price_from": 29, "carrier": "TGV/Ouigo"},
        {"mode": "bus", "hours": 6.5, "price_from": 20, "carrier": "FlixBus"},
    ],
    ("PAR", "BCN"): [
        {"mode": "train", "hours": 6.8, "price_from": 59, "carrier": "TGV/Renfe"},
        {"mode": "bus", "hours": 14.5, "price_from": 40, "carrier": "FlixBus"},
    ],
    ("PAR", "BER"): [
        {"mode": "train", "hours": 8.0, "price_from": 60, "carrier": "ICE/TGV"},
        {"mode": "bus", "hours": 13.0, "price_from": 45, "carrier": "FlixBus"},
    ],
}

def get_ground_options(origin: str, dest: str):
    return GROUND_ROUTES.get((origin, dest), [])