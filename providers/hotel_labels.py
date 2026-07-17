# Libellés d'hébergement FR / EN / ES.
# Formulés comme "budget" (estimation honnête), pas comme un prix constaté.

LABELS = {
    "hotel": {"fr": "Budget hébergement", "en": "Lodging budget",
              "es": "Presupuesto alojamiento"},
    "hostel": {"fr": "Budget auberge", "en": "Hostel budget",
               "es": "Presupuesto albergue"},
    "any": {"fr": "Budget hébergement", "en": "Lodging budget",
            "es": "Presupuesto alojamiento"},
}

def hotel_label(acc: str, lang: str) -> str:
    labels = LABELS.get(acc, LABELS["hotel"])
    return labels.get(lang, labels["en"])