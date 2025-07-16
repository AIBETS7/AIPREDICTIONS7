import requests
from bs4 import BeautifulSoup
import json
import os
import time

SOFA_URL = 'https://www.sofascore.com/football'
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'data', 'sofascore_stats.json')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'https://www.google.com/'
}

def scrape_sofascore():
    time.sleep(1)  # Pequeño retardo para evitar bloqueos
    resp = requests.get(SOFA_URL, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    matches = []
    for event in soup.select('a.sc-hLBbgP'):
        href = event.get('href')
        if href and isinstance(href, str):
            match = {
                'url': 'https://www.sofascore.com' + href,
                'teams': event.text.strip() if event.text else ''
            }
            matches.append(match)
    return matches

def main():
    matches = scrape_sofascore()
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)
    print(f"Estadísticas guardadas en {OUTPUT_PATH}")

if __name__ == "__main__":
    main() 