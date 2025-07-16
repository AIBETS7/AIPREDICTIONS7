import requests
from bs4 import BeautifulSoup
import json
import os

FLASH_URL = 'https://www.flashscore.com/'
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'data', 'flashscore_fixtures.json')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def scrape_flashscore():
    resp = requests.get(FLASH_URL, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    matches = []
    # Buscar partidos en la portada (puede requerir ajuste si cambia la estructura)
    for event in soup.select('div.event__match'):  # Selector típico de Flashscore
        match = {
            'id': event.get('id'),
            'time': event.select_one('.event__time').text if event.select_one('.event__time') else '',
            'home': event.select_one('.event__participant--home').text if event.select_one('.event__participant--home') else '',
            'away': event.select_one('.event__participant--away').text if event.select_one('.event__participant--away') else '',
            'score': event.select_one('.event__scores').text if event.select_one('.event__scores') else ''
        }
        matches.append(match)
    return matches

def main():
    matches = scrape_flashscore()
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)
    print(f"Partidos guardados en {OUTPUT_PATH}")

if __name__ == "__main__":
    main() 