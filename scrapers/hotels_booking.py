from typing import List, Optional
import asyncio
import re
from playwright.async_api import async_playwright
from datetime import datetime, timedelta

PRICE_REGEX = re.compile(r"(?:C\$|\$|€)?\s?([0-9]{1,4}(?:[,\.][0-9]{3})*(?:[,\.][0-9]{2})?)")
RATING_REGEX = re.compile(r"(\d+\.?\d*)\s*(?:/\s*10)?")

def parse_price(s: str) -> Optional[float]:
    """Convertit une chaîne de prix en nombre"""
    s = s.replace(" ", "")
    # Format européen : 1.234,56 → 1234.56
    if s.count(",") == 1 and s.count(".") > 0:
        s = s.replace(".", "").replace(",", ".")
    # Format nord-américain : 1,234.56 → 1234.56
    else:
        s = s.replace(",", "")
    
    try:
        return float(s)
    except:
        return None

def parse_period_to_dates(period: str, nights: int) -> tuple:
    """Convertir 'Octobre 2026' en dates check-in/check-out"""
    months = {
        'Janvier': 1, 'Février': 2, 'Mars': 3, 'Avril': 4, 'Mai': 5, 'Juin': 6,
        'Juillet': 7, 'Août': 8, 'Septembre': 9, 'Octobre': 10, 'Novembre': 11, 'Décembre': 12
    }
    
    month_name, year = period.split(' ')
    month = months[month_name]
    
    # Prendre le milieu du mois pour check-in
    checkin_date = datetime(int(year), month, 15)
    checkout_date = checkin_date + timedelta(days=nights)
    
    return (
        checkin_date.strftime("%Y-%m-%d"),
        checkout_date.strftime("%Y-%m-%d")
    )

async def scrape_hotels_booking(
    city_code: str,
    max_price_per_night: float,
    nights: int,
    period: str,
    min_rating: int = 0,
    accommodation_type: str = "all"
) -> List[dict]:
    """
    Scrape RÉEL de Booking.com
    """
    
    print(f"🏨 Scraping hotels in {city_code}")
    print(f"   Max price/night: {max_price_per_night:.0f} CAD")
    print(f"   Nights: {nights}")
    print(f"   Min rating: {min_rating}★")
    print(f"   Type: {accommodation_type}")
    
    # Convertir la période en dates
    checkin, checkout = parse_period_to_dates(period, nights)
    
    # Construire l'URL Booking.com avec filtres
    base_url = "https://www.booking.com/searchresults.html"
    
    # Mapping code aéroport → nom de ville pour Booking
    city_names = {
        'BCN': 'Barcelona', 'LIS': 'Lisbon', 'MAD': 'Madrid', 'FCO': 'Rome',
        'CDG': 'Paris', 'LHR': 'London', 'DUB': 'Dublin', 'AMS': 'Amsterdam',
        'BER': 'Berlin', 'PRG': 'Prague', 'ATH': 'Athens', 'VIE': 'Vienna',
        'MEX': 'Mexico City', 'BOG': 'Bogota', 'LIM': 'Lima'
    }
    
    city_name = city_names.get(city_code, city_code)
    
    # URL avec filtres
    url = f"{base_url}?ss={city_name}&checkin={checkin}&checkout={checkout}&group_adults=1&no_rooms=1"
    
    # Filtre type d'hébergement
    if accommodation_type == "hotel":
        url += "&nflt=ht_id%3D204"  # Hotels seulement
    elif accommodation_type == "hostel":
        url += "&nflt=ht_id%3D203"  # Hostels
    elif accommodation_type == "apartment":
        url += "&nflt=ht_id%3D201"  # Apartments
    
    print(f"   URL: {url}")
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                locale='en-CA',
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            # Aller sur la page
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Rejeter les cookies
            try:
                await page.click('button[aria-label*="Dismiss"]', timeout=3000)
            except:
                try:
                    await page.click('button:has-text("Reject")', timeout=2000)
                except:
                    pass
            
            # Attendre que les résultats chargent
            await asyncio.sleep(5)
            
            # Scroller pour charger plus de résultats
            for _ in range(3):
                await page.mouse.wheel(0, 1500)
                await asyncio.sleep(1)
            
            # Extraire les cartes d'hôtels
            hotels = []
            
            # Sélecteurs pour les éléments (peuvent changer, à adapter)
            hotel_cards = await page.query_selector_all('[data-testid="property-card"]')
            
            print(f"   Found {len(hotel_cards)} hotel cards")
            
            for card in hotel_cards[:15]:  # Limiter à 15 résultats
                try:
                    # Nom de l'hôtel
                    name_elem = await card.query_selector('[data-testid="title"]')
                    name = await name_elem.inner_text() if name_elem else "Unknown Hotel"
                    
                    # Prix
                    price_elem = await card.query_selector('[data-testid="price-and-discounted-price"]')
                    if not price_elem:
                        price_elem = await card.query_selector('.prco-valign-middle-helper')
                    
                    if price_elem:
                        price_text = await price_elem.inner_text()
                        # Extraire le nombre du prix
                        price_match = PRICE_REGEX.search(price_text)
                        if price_match:
                            total_price = parse_price(price_match.group(1))
                            if total_price:
                                price_per_night = total_price / nights
                            else:
                                continue
                        else:
                            continue
                    else:
                        continue
                    
                    # Filtrer par prix
                    if price_per_night > max_price_per_night:
                        continue
                    
                    # Note
                    rating = 0.0
                    rating_elem = await card.query_selector('[data-testid="review-score"]')
                    if rating_elem:
                        rating_text = await rating_elem.inner_text()
                        rating_match = RATING_REGEX.search(rating_text)
                        if rating_match:
                            rating = float(rating_match.group(1))
                    
                    # Filtrer par note
                    if min_rating > 0:
                        # Booking utilise /10, nous utilisons /5
                        rating_out_of_5 = rating / 2
                        if rating_out_of_5 < min_rating:
                            continue
                    
                    # URL de l'hôtel
                    link_elem = await card.query_selector('a[data-testid="title-link"]')
                    hotel_url = await link_elem.get_attribute('href') if link_elem else ""
                    
                    # Générer URL d'affiliation
                    # Format Booking : ?aid=YOUR_AFFILIATE_ID
                    affiliate_id = "YOUR_BOOKING_AFFILIATE_ID"  # À remplacer
                    if hotel_url:
                        if '?' in hotel_url:
                            affiliate_url = f"{hotel_url}&aid={affiliate_id}"
                        else:
                            affiliate_url = f"{hotel_url}?aid={affiliate_id}"
                    else:
                        affiliate_url = f"https://www.booking.com?aid={affiliate_id}"
                    
                    # Déterminer le type
                    acc_type = "hotel"  # Par défaut
                    if "hostel" in name.lower():
                        acc_type = "hostel"
                    elif "apartment" in name.lower() or "apart" in name.lower():
                        acc_type = "apartment"
                    
                    hotels.append({
                        "name": name,
                        "price_per_night": round(price_per_night, 2),
                        "rating": rating / 2,  # Convertir de /10 à /5
                        "accommodation_type": acc_type,
                        "affiliate_url": affiliate_url
                    })
                    
                except Exception as e:
                    print(f"   Error parsing hotel card: {e}")
                    continue
            
            await browser.close()
            
            print(f"   ✅ Scraped {len(hotels)} hotels successfully")
            
            # Trier par meilleur rapport qualité/prix
            if hotels:
                hotels.sort(key=lambda x: x["rating"] / x["price_per_night"], reverse=True)
            
            return hotels
            
        except Exception as e:
            print(f"   ❌ Error scraping Booking.com: {e}")
            
            # FALLBACK vers mock data si le scraping échoue
            return get_mock_hotels(city_code, max_price_per_night, min_rating, accommodation_type)

def get_mock_hotels(city_code: str, max_price: float, min_rating: int, acc_type: str) -> List[dict]:
    """Données mock de fallback"""
    mock_hotels = {
        'BCN': [
            {"name": "Hotel Catalonia", "price_per_night": 85, "rating": 4.2, "accommodation_type": "hotel"},
            {"name": "Barcelona Hostel", "price_per_night": 35, "rating": 3.8, "accommodation_type": "hostel"},
            {"name": "Gothic Quarter Apartment", "price_per_night": 95, "rating": 4.5, "accommodation_type": "apartment"},
        ],
        'LIS': [
            {"name": "Lisbon Central Hotel", "price_per_night": 70, "rating": 4.0, "accommodation_type": "hotel"},
            {"name": "Alfama Hostel", "price_per_night": 30, "rating": 3.9, "accommodation_type": "hostel"},
        ],
        'CDG': [
            {"name": "Paris Marais Hotel", "price_per_night": 120, "rating": 4.3, "accommodation_type": "hotel"},
            {"name": "Montmartre Apartment", "price_per_night": 110, "rating": 4.4, "accommodation_type": "apartment"},
        ],
        'FCO': [
            {"name": "Roma Centro Hotel", "price_per_night": 95, "rating": 4.1, "accommodation_type": "hotel"},
        ],
        'MEX': [
            {"name": "Mexico City Hotel", "price_per_night": 60, "rating": 4.2, "accommodation_type": "hotel"},
        ],
    }
    
    city_hotels = mock_hotels.get(city_code, [
        {"name": f"{city_code} Hotel", "price_per_night": 80, "rating": 4.0, "accommodation_type": "hotel"}
    ])
    
    # Appliquer les filtres
    filtered = []
    for hotel in city_hotels:
        if hotel["price_per_night"] > max_price:
            continue
        if hotel["rating"] < min_rating:
            continue
        if acc_type != "all" and hotel["accommodation_type"] != acc_type:
            continue
        
        affiliate_url = f"https://www.booking.com?aid=YOUR_AFFILIATE_ID"
        hotel["affiliate_url"] = affiliate_url
        filtered.append(hotel)
    
    return filtered
```

---

## ÉTAPE 4 : Inscription Booking.com Affiliation

### A. S'inscrire

1. **Va sur https://www.booking.com/affiliate-program/v2/index.html**
2. **Apply now**
3. **Remplis le formulaire :**
   - Website: `https://flights2go.app`
   - Description: "Budget-based travel discovery platform"
   - Traffic: "0-10,000/month"

4. **Attends l'approbation (1-3 jours)**

### B. Récupère ton Affiliate ID

Une fois approuvé, tu reçois un ID comme :
```
1234567