# Destinations européennes — noms localisés FR / EN / ES

def D(code, fr, en, es, cfr, cen, ces, flag, slug):
    return {
        "names": {"fr": fr, "en": en, "es": es},
        "country": {"fr": cfr, "en": cen, "es": ces},
        "flag": flag, "slug": slug,
    }

DESTINATIONS = {
    # Espagne
    "BCN": D("BCN", "Barcelone", "Barcelona", "Barcelona", "Espagne", "Spain", "España", "🇪🇸", "barcelona"),
    "MAD": D("MAD", "Madrid", "Madrid", "Madrid", "Espagne", "Spain", "España", "🇪🇸", "madrid"),
    "VLC": D("VLC", "Valence", "Valencia", "Valencia", "Espagne", "Spain", "España", "🇪🇸", "valencia"),
    "SVQ": D("SVQ", "Séville", "Seville", "Sevilla", "Espagne", "Spain", "España", "🇪🇸", "seville"),
    "AGP": D("AGP", "Malaga", "Malaga", "Málaga", "Espagne", "Spain", "España", "🇪🇸", "malaga"),
    "BIO": D("BIO", "Bilbao", "Bilbao", "Bilbao", "Espagne", "Spain", "España", "🇪🇸", "bilbao"),
    "PMI": D("PMI", "Palma de Majorque", "Palma de Mallorca", "Palma de Mallorca", "Espagne", "Spain", "España", "🇪🇸", "palma-mallorca"),
    "IBZ": D("IBZ", "Ibiza", "Ibiza", "Ibiza", "Espagne", "Spain", "España", "🇪🇸", "ibiza"),
    # Portugal
    "LIS": D("LIS", "Lisbonne", "Lisbon", "Lisboa", "Portugal", "Portugal", "Portugal", "🇵🇹", "lisbon"),
    "OPO": D("OPO", "Porto", "Porto", "Oporto", "Portugal", "Portugal", "Portugal", "🇵🇹", "porto"),
    "FAO": D("FAO", "Faro", "Faro", "Faro", "Portugal", "Portugal", "Portugal", "🇵🇹", "faro"),
    # France
    "PAR": D("PAR", "Paris", "Paris", "París", "France", "France", "Francia", "🇫🇷", "paris"),
    "MRS": D("MRS", "Marseille", "Marseille", "Marsella", "France", "France", "Francia", "🇫🇷", "marseille"),
    "LYS": D("LYS", "Lyon", "Lyon", "Lyon", "France", "France", "Francia", "🇫🇷", "lyon"),
    "NCE": D("NCE", "Nice", "Nice", "Niza", "France", "France", "Francia", "🇫🇷", "nice"),
    "TLS": D("TLS", "Toulouse", "Toulouse", "Toulouse", "France", "France", "Francia", "🇫🇷", "toulouse"),
    "BOD": D("BOD", "Bordeaux", "Bordeaux", "Burdeos", "France", "France", "Francia", "🇫🇷", "bordeaux"),
    # Royaume-Uni / Irlande
    "LON": D("LON", "Londres", "London", "Londres", "Royaume-Uni", "United Kingdom", "Reino Unido", "🇬🇧", "london"),
    "EDI": D("EDI", "Édimbourg", "Edinburgh", "Edimburgo", "Royaume-Uni", "United Kingdom", "Reino Unido", "🇬🇧", "edinburgh"),
    "DUB": D("DUB", "Dublin", "Dublin", "Dublín", "Irlande", "Ireland", "Irlanda", "🇮🇪", "dublin"),
    # Benelux
    "AMS": D("AMS", "Amsterdam", "Amsterdam", "Ámsterdam", "Pays-Bas", "Netherlands", "Países Bajos", "🇳🇱", "amsterdam"),
    "BRU": D("BRU", "Bruxelles", "Brussels", "Bruselas", "Belgique", "Belgium", "Bélgica", "🇧🇪", "brussels"),
    # Allemagne / Suisse / Autriche
    "BER": D("BER", "Berlin", "Berlin", "Berlín", "Allemagne", "Germany", "Alemania", "🇩🇪", "berlin"),
    "MUC": D("MUC", "Munich", "Munich", "Múnich", "Allemagne", "Germany", "Alemania", "🇩🇪", "munich"),
    "HAM": D("HAM", "Hambourg", "Hamburg", "Hamburgo", "Allemagne", "Germany", "Alemania", "🇩🇪", "hamburg"),
    "ZRH": D("ZRH", "Zurich", "Zurich", "Zúrich", "Suisse", "Switzerland", "Suiza", "🇨🇭", "zurich"),
    "GVA": D("GVA", "Genève", "Geneva", "Ginebra", "Suisse", "Switzerland", "Suiza", "🇨🇭", "geneva"),
    "VIE": D("VIE", "Vienne", "Vienna", "Viena", "Autriche", "Austria", "Austria", "🇦🇹", "vienna"),
    # Italie
    "ROM": D("ROM", "Rome", "Rome", "Roma", "Italie", "Italy", "Italia", "🇮🇹", "rome"),
    "MIL": D("MIL", "Milan", "Milan", "Milán", "Italie", "Italy", "Italia", "🇮🇹", "milan"),
    "VCE": D("VCE", "Venise", "Venice", "Venecia", "Italie", "Italy", "Italia", "🇮🇹", "venice"),
    "FLR": D("FLR", "Florence", "Florence", "Florencia", "Italie", "Italy", "Italia", "🇮🇹", "florence"),
    "NAP": D("NAP", "Naples", "Naples", "Nápoles", "Italie", "Italy", "Italia", "🇮🇹", "naples"),
    "PMO": D("PMO", "Palerme", "Palermo", "Palermo", "Italie", "Italy", "Italia", "🇮🇹", "palermo"),
    # Europe centrale / de l'Est
    "PRG": D("PRG", "Prague", "Prague", "Praga", "Tchéquie", "Czechia", "Chequia", "🇨🇿", "prague"),
    "BUD": D("BUD", "Budapest", "Budapest", "Budapest", "Hongrie", "Hungary", "Hungría", "🇭🇺", "budapest"),
    "KRK": D("KRK", "Cracovie", "Krakow", "Cracovia", "Pologne", "Poland", "Polonia", "🇵🇱", "krakow"),
    "WAW": D("WAW", "Varsovie", "Warsaw", "Varsovia", "Pologne", "Poland", "Polonia", "🇵🇱", "warsaw"),
    "BTS": D("BTS", "Bratislava", "Bratislava", "Bratislava", "Slovaquie", "Slovakia", "Eslovaquia", "🇸🇰", "bratislava"),
    "BUH": D("BUH", "Bucarest", "Bucharest", "Bucarest", "Roumanie", "Romania", "Rumanía", "🇷🇴", "bucharest"),
    "SOF": D("SOF", "Sofia", "Sofia", "Sofía", "Bulgarie", "Bulgaria", "Bulgaria", "🇧🇬", "sofia"),
    # Balkans / Adriatique
    "ZAG": D("ZAG", "Zagreb", "Zagreb", "Zagreb", "Croatie", "Croatia", "Croacia", "🇭🇷", "zagreb"),
    "SPU": D("SPU", "Split", "Split", "Split", "Croatie", "Croatia", "Croacia", "🇭🇷", "split"),
    "DBV": D("DBV", "Dubrovnik", "Dubrovnik", "Dubrovnik", "Croatie", "Croatia", "Croacia", "🇭🇷", "dubrovnik"),
    "LJU": D("LJU", "Ljubljana", "Ljubljana", "Liubliana", "Slovénie", "Slovenia", "Eslovenia", "🇸🇮", "ljubljana"),
    # Grèce / Malte
    "ATH": D("ATH", "Athènes", "Athens", "Atenas", "Grèce", "Greece", "Grecia", "🇬🇷", "athens"),
    "MLA": D("MLA", "Malte", "Malta", "Malta", "Malte", "Malta", "Malta", "🇲🇹", "malta"),
    # Scandinavie / Baltique
    "CPH": D("CPH", "Copenhague", "Copenhagen", "Copenhague", "Danemark", "Denmark", "Dinamarca", "🇩🇰", "copenhagen"),
    "OSL": D("OSL", "Oslo", "Oslo", "Oslo", "Norvège", "Norway", "Noruega", "🇳🇴", "oslo"),
    "STO": D("STO", "Stockholm", "Stockholm", "Estocolmo", "Suède", "Sweden", "Suecia", "🇸🇪", "stockholm"),
    "HEL": D("HEL", "Helsinki", "Helsinki", "Helsinki", "Finlande", "Finland", "Finlandia", "🇫🇮", "helsinki"),
    "TLL": D("TLL", "Tallinn", "Tallinn", "Tallin", "Estonie", "Estonia", "Estonia", "🇪🇪", "tallinn"),
    "RIX": D("RIX", "Riga", "Riga", "Riga", "Lettonie", "Latvia", "Letonia", "🇱�🇻", "riga"),
}

VALID_LANGS = ("fr", "en", "es")

def localize(code: str, lang: str) -> dict:
    d = DESTINATIONS[code]
    lg = lang if lang in VALID_LANGS else "en"
    return {
        "code": code,
        "name": d["names"][lg],
        "country": d["country"][lg],
        "flag": d["flag"],
        "slug": d["slug"],
    }