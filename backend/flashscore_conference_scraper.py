import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

FLASHCORE_URL = 'https://www.flashscore.es/futbol/europa/conference-league/partidos/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'https://www.google.com/'
}

def get_conference_matches_tomorrow():
    resp = requests.get(FLASHCORE_URL, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    matches = []
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    # Buscar todos los partidos en el HTML (aunque estén en bloques dinámicos)
    for match_row in soup.find_all('div', class_=re.compile('event__match')):
        # Extraer fecha del partido (puede estar en un atributo data-date o buscar el bloque de fecha anterior)
        date_block = match_row.find_previous('div', class_='event__header')
        if date_block:
            date_text = date_block.get_text(strip=True)
            try:
                match_date = datetime.strptime(date_text, '%d.%m.%Y').date()
            except Exception:
                continue
            if match_date != tomorrow:
                continue
        else:
            continue
        # Extraer equipos y hora
        home = match_row.find('div', class_='event__participant--home')
        away = match_row.find('div', class_='event__participant--away')
        time_div = match_row.find('div', class_='event__time')
        if home and away and time_div:
            matches.append({
                'home_team': home.get_text(strip=True),
                'away_team': away.get_text(strip=True),
                'time': time_div.get_text(strip=True),
                'date': match_date.strftime('%Y-%m-%d')
            })
    return matches

if __name__ == "__main__":
    partidos = get_conference_matches_tomorrow()
    for p in partidos:
        print(p) 