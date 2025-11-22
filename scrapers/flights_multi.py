from typing import List, Optional
import asyncio
from datetime import datetime, timedelta
import re
from playwright.async_api import async_playwright

PRICE_REGEX = re.compile(r"(?:C\$|\$)?\s?([0-9]{2,4}(?:[,][0-9]{3})*)")

DESTINATIONS_INFO = {
    # Europe
    'BCN': {'city': 'Barcelone', 'country': 'Espagne', 'flag': '🇪🇸'},
    'LIS': {'city': 'Lisbonne', 'country': 'Portugal', 'flag': '🇵🇹'},
    'MAD': {'city': 'Madrid', 'country': 'Espagne', 'flag': '🇪🇸'},
    'FCO': {'city': 'Rome', 'country': 'Italie', 'flag': '🇮🇹'},
    'CDG': {'city': 'Paris', 'country': 'France', 'flag': '🇫🇷'},
    'LHR': {'city': 'Londres', 'country': 'Royaume-Uni', 'flag': '🇬🇧'},
    'DUB': {'city': 'Dublin', 'country': 'Irlande', 'flag': '🇮🇪'},
    'AMS': {'city': 'Amsterdam', 'country': 'Pays-Bas', 'flag': '🇳🇱'},
    'BER': {'city': 'Berlin', 'country': 'Allemagne', 'flag': '🇩🇪'},
    'PRG': {'city': 'Prague', 'country': 'République tchèque', 'flag': '🇨🇿'},
    'ATH': {'city': 'Athènes', 'country': 'Grèce', 'flag': '🇬🇷'},
    'VIE': {'city': 'Vienne', 'country': 'Autriche', 'flag': '🇦🇹'},
    'BUD': {'city': 'Budapest', 'country': 'Hongrie', 'flag': '🇭🇺'},
    'WAW': {'city': 'Varsovie', 'country': 'Pologne', 'flag': '🇵🇱'},
    'CPH': {'city': 'Copenhague', 'country': 'Danemark', 'flag': '🇩🇰'},
    'OSL': {'city': 'Oslo', 'country': 'Norvège', 'flag': '🇳🇴'},
    'STO': {'city': 'Stockholm', 'country': 'Suède', 'flag': '🇸🇪'},
    'HEL': {'city': 'Helsinki', 'country': 'Finlande', 'flag': '🇫🇮'},
    'ZRH': {'city': 'Zurich', 'country': 'Suisse', 'flag': '🇨🇭'},
    'MUC': {'city': 'Munich', 'country': 'Allemagne', 'flag': '🇩🇪'},
    'BRU': {'city': 'Bruxelles', 'country': 'Belgique', 'flag': '🇧🇪'},
    'VCE': {'city': 'Venise', 'country': 'Italie', 'flag': '🇮🇹'},
    'NAP': {'city': 'Naples', 'country': 'Italie', 'flag': '🇮🇹'},
    'MXP': {'city': 'Milan', 'country': 'Italie', 'flag': '🇮🇹'},
    'OPO': {'city': 'Porto', 'country': 'Portugal', 'flag': '🇵🇹'},
    
    # Amérique
    'MEX': {'city': 'Mexico City', 'country': 'Mexique', 'flag': '🇲🇽'},
    'BOG': {'city': 'Bogotá', 'country': 'Colombie', 'flag': '🇨🇴'},
    'LIM': {'city': 'Lima', 'country': 'Pérou', 'flag': '🇵🇪'},
    'GRU': {'city': 'São Paulo', 'country': 'Brésil', 'flag': '🇧🇷'},
    'EZE': {'city': 'Buenos Aires', 'country': 'Argentine', 'flag': '🇦🇷'},
    'SCL': {'city': 'Santiago', 'country': 'Chili', 'flag': '🇨🇱'},
    'PTY': {'city': 'Panama City', 'country': 'Panama', 'flag': '🇵🇦'},
    'CUN': {'city': 'Cancún', 'country': 'Mexique', 'flag': '🇲🇽'},
    'GDL': {'city': 'Guadalajara', 'country': 'Mexique', 'flag': '🇲🇽'},
    'MDE': {'city': 'Medellín', 'country': 'Colombie', 'flag': '🇨🇴'},
    
    # Asie
    'NRT': {'city': 'Tokyo', 'country': 'Japon', 'flag': '🇯🇵'},
    'ICN': {'city': 'Seoul', 'country': 'Corée du Sud', 'flag': '🇰🇷'},
    'BKK': {'city': 'Bangkok', 'country': 'Thaïlande', 'flag': '🇹🇭'},
    'SIN': {'city': 'Singapour', 'country': 'Singapour', 'flag': '🇸🇬'},
    'HKG': {'city': 'Hong Kong', 'country': 'Hong Kong', 'flag': '🇭🇰'},
    'DEL': {'city': 'Delhi', 'country': 'Inde', 'flag': '🇮🇳'},
    'BOM': {'city': 'Mumbai', 'country': 'Inde', 'flag': '🇮🇳'},
    'DXB': {'city': 'Dubaï', 'country': 'Émirats arabes unis', 'flag': '🇦🇪'},
}

def parse_price(s: str) -> Optional[float]:
    s = s.replace(" ", "").replace(",", "")
    try:
        return float(s)
    except:
        return None

def parse_period(period: str) -> tuple:
    months = {
        'Janvier': 1, 'Février': 2, 'Mars': 3, 'Avril': 4, 'Mai': 5, 'Juin': 6,
        'Juillet': 7, 'Août': 8, 'Septembre': 9, 'Octobre': 10, 'Novembre': 11, 'Décembre': 12
    }
    
    month_name, year = period.split(' ')
    month = months[month_name]
    
    start_date = f"{year}-{month:02d}-01"
    
    if month == 12:
        next_month = datetime(int(year) + 1, 1, 1)
    else:
        next_month = datetime(int(year), month + 1, 1)
    last_day = (next_month - timedelta(days=1)).day
    end_date = f"{year}-{month:02d}-{last_day}"
    
    return start_date, end_date

async def scrape_kayak_price(origin: str, dest: str, date: str, max_stops: int) -> Optional[dict]:
    """
    Scrape Kayak pour un vol spécifique
    Retourne: {price, stops, duration_hours, has_baggage}
    """
    # Construire l'URL avec filtre d'escales
    stops_filter = ""
    if max_stops == 0:
        stops_filter = "&fs=stops=0"
    elif max_stops == 1:
        stops_filter = "&fs=stops=~0;1"
    elif max_stops == 2:
        stops_filter = "&fs=stops=~0;1;2"
    
    url = f"https://www.kayak.com/flights/{origin}-{dest}/{date}?sort=price_a{stops_filter}"
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            try:
                await page.click('button:has-text("Reject")', timeout=2000)
            except:
                pass
            
            await asyncio.sleep(5)
            for _ in range(3):
                await page.mouse.wheel(0, 1000)
                await asyncio.sleep(0.5)
            
            body_text = await page.inner_text("body")
            await browser.close()
            
            # Extraire les prix
            prices = []
            for match in PRICE_REGEX.finditer(body_text):
                price = parse_price(match.group(1))
                if price and 50 <= price <= 5000:
                    prices.append(price)
            
            if not prices:
                return None
            
            min_price = min(prices)
            
            # Déterminer le nombre d'escales (approximatif)
            # En vrai, il faudrait parser le HTML pour être précis
            stops = 0 if "Direct" in body_text or "Nonstop" in body_text else 1
            
            # Durée approximative (à améliorer avec parsing HTML)
            duration_hours = estimate_flight_duration(origin, dest)
            
            # Bagages (approximatif)
            has_baggage = "baggage included" in body_text.lower()
            
            return {
                "price": min_price,
                "stops": stops,
                "duration_hours": duration_hours,
                "has_baggage": has_baggage
            }
            
        except Exception as e:
            print(f"Error scraping {origin}-{dest}: {e}")
            return None

def estimate_flight_duration(origin: str, dest: str) -> float:
    """Estimation grossière de la durée de vol en heures"""
    # Distance approximative en km (à améliorer avec une vraie DB)
    distances = {
        # Europe depuis YUL
        ('YUL', 'BCN'): 6000, ('YUL', 'LIS'): 5500, ('YUL', 'CDG'): 5500,
        ('YUL', 'FCO'): 6500, ('YUL', 'LHR'): 5200, ('YUL', 'AMS'): 5700,
        # Amérique depuis YUL
        ('YUL', 'MEX'): 3500, ('YUL', 'BOG'): 4500, ('YUL', 'LIM'): 6000,
        # Asie depuis YUL
        ('YUL', 'NRT'): 10500, ('YUL', 'BKK'): 13000, ('YUL', 'SIN'): 15000,
    }
    
    distance = distances.get((origin, dest), 6000)  # Default 6000km
    speed = 800  # km/h moyenne
    return round(distance / speed, 1)

async def scrape_flights_multi(
    origin: str,
    max_budget: float,
    period: str,
    destinations: List[str],
    max_stops: int = -1,
    max_duration: int = -1,
    baggage_included: bool = False
) -> List[dict]:
    """
    Scrape plusieurs destinations avec filtres
    """
    start_date, end_date = parse_period(period)
    
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    delta = (end - start).days
    
    # Échantillonner 5 dates dans la période
    sample_dates = []
    for i in range(min(5, delta + 1)):
        offset = (delta // 5) * i if delta >= 5 else i
        sample_date = (start + timedelta(days=offset)).strftime("%Y-%m-%d")
        sample_dates.append(sample_date)
    
    results = []
    
    for dest_code in destinations:
        dest_info = DESTINATIONS_INFO.get(dest_code)
        if not dest_info:
            continue
        
        try:
            # Scraper les dates en parallèle
            tasks = [scrape_kayak_price(origin, dest_code, date, max_stops) for date in sample_dates]
            prices_data = await asyncio.gather(*tasks)
            
            # Filtrer les résultats valides
            valid_prices = [p for p in prices_data if p is not None]
            
            if not valid_prices:
                continue
            
            # Prendre le vol le moins cher
            best_flight = min(valid_prices, key=lambda x: x["price"])
            
            # Appliquer les filtres
            if best_flight["price"] > max_budget:
                continue
            
            if max_stops >= 0 and best_flight["stops"] > max_stops:
                continue
            
            if max_duration > 0 and best_flight["duration_hours"] > max_duration:
                continue
            
            if baggage_included and not best_flight["has_baggage"]:
                continue
            
            # Générer l'URL d'affiliation Kayak
            affiliate_url = f"https://www.kayak.com/flights/{origin}-{dest_code}?a=kan_YOUR_AFFILIATE_ID"
            
            results.append({
                "city": dest_info['city'],
                "country": dest_info['country'],
                "code": dest_code,
                "flag": dest_info['flag'],
                "price": best_flight["price"],
                "stops": best_flight["stops"],
                "duration_hours": best_flight["duration_hours"],
                "has_baggage": best_flight["has_baggage"],
                "airline": None,  # TODO: parser le nom de la compagnie
                "affiliate_url": affiliate_url
            })
            
        except Exception as e:
            print(f"Error on {dest_code}: {e}")
            continue
    
    # Trier par prix
    return sorted(results, key=lambda x: x['price'])