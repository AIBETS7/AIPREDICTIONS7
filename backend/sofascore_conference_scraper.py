import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

SOFASCORE_URL = 'https://www.sofascore.com/es/futbol/europa/uefa-europa-conference-league'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'https://www.google.com/'
}

def get_conference_matches_tomorrow_sofa():
    resp = requests.get(SOFASCORE_URL, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    matches = []
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    # Buscar partidos por fecha en el HTML
    for match_row in soup.find_all('a', href=re.compile('/partido/')):
        # Extraer fecha y hora del partido (puede estar en un atributo data-date o en el texto)
        date_div = match_row.find('div', class_=re.compile('Cell__Date'))
        time_div = match_row.find('div', class_=re.compile('Cell__Time'))
        home = match_row.find('div', class_=re.compile('Cell__Participant--home'))
        away = match_row.find('div', class_=re.compile('Cell__Participant--away'))
        if not (date_div and time_div and home and away):
            continue
        # Parsear fecha
        try:
            match_date = datetime.strptime(date_div.get_text(strip=True), '%d.%m.%Y').date()
        except Exception:
            continue
        if match_date != tomorrow:
            continue
        matches.append({
            'home_team': home.get_text(strip=True),
            'away_team': away.get_text(strip=True),
            'time': time_div.get_text(strip=True),
            'date': match_date.strftime('%Y-%m-%d')
        })
    return matches

if __name__ == "__main__":
    partidos = get_conference_matches_tomorrow_sofa()
    for p in partidos:
        print(p) 