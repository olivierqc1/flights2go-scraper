from typing import List, Optional
import asyncio
from datetime import datetime, timedelta
import re
from playwright.async_api import async_playwright

PRICE_REGEX = re.compile(r"(?:C\$|\$)?\s?([0-9]{2,4}(?:[,][0-9]{3})*)")

DESTINATIONS = {
    'BCN': {'city': 'Barcelone', 'country': 'Espagne', 'flag': '🇪🇸'},
    'LIS': {'city': 'Lisbonne', 'country': 'Portugal', 'flag': '🇵🇹'},
    'MAD': {'city': 'Madrid', 'country': 'Espagne', 'flag': '🇪🇸'},
    'FCO': {'city': 'Rome', 'country': 'Italie', 'flag': '🇮🇹'},
    'CDG': {'city': 'Paris', 'country': 'France', 'flag': '🇫🇷'},
    'LHR': {'city': 'Londres', 'country': 'Royaume-Uni', 'flag': '🇬🇧'},
    'DUB': {'city': 'Dublin', 'country': 'Irlande', 'flag': '🇮🇪'},
    'AMS': {'city': 'Amsterdam', 'country': 'Pays-Bas', 'flag': '🇳🇱'},
    'MEX': {'city': 'Mexico City', 'country': 'Mexique', 'flag': '🇲🇽'},
    'BOG': {'city': 'Bogotá', 'country': 'Colombie', 'flag': '🇨🇴'},
}

def parse_price(s: str) -> Optional[float]:
    s = s.replace(" ", "").replace(",", "")
    try:
        return float(s)
    except:
        return None

async def scrape_kayak_price(origin: str, dest: str, date: str) -> Optional[float]:
    url = f"https://www.kayak.com/flights/{origin}-{dest}/{date}?sort=price_a&fs=stops=0"
    
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
            
            prices = []
            for match in PRICE_REGEX.finditer(body_text):
                price = parse_price(match.group(1))
                if price and 50 <= price <= 5000:
                    prices.append(price)
            
            return min(prices) if prices else None
            
        except Exception as e:
            print(f"Error scraping {dest}: {e}")
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

async def scrape_flights_kayak(origin: str, budget: float, period: str) -> List[dict]:
    """Scrape Kayak pour tous les vols dans le budget"""
    
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
    
    for dest_code, dest_info in DESTINATIONS.items():
        # Scraper les dates en parallèle
        tasks = [scrape_kayak_price(origin, dest_code, date) for date in sample_dates]
        prices = await asyncio.gather(*tasks)
        
        valid_prices = [p for p in prices if p is not None]
        
        if not valid_prices:
            continue
        
        best_price = min(valid_prices)
        
        if best_price > budget:
            continue
        
        # Générer l'URL d'affiliation
        affiliate_url = f"https://www.kayak.com/flights/{origin}-{dest_code}?a=kan_YOUR_ID"
        
        results.append({
            "type": "flight",
            "city": dest_info['city'],
            "country": dest_info['country'],
            "code": dest_code,
            "price": best_price,
            "currency": "CAD",
            "flag": dest_info['flag'],
            "affiliate_url": affiliate_url
        })
    
    return sorted(results, key=lambda x: x['price'])