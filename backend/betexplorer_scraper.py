import requests
from bs4 import BeautifulSoup
import json
import os

BETEXPLORER_URL = 'https://www.betexplorer.com/soccer/'
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'data', 'betexplorer_stats.json')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def scrape_betexplorer():
    resp = requests.get(BETEXPLORER_URL, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    matches = []
    # Buscar partidos en la portada (puede requerir ajuste si cambia la estructura)
    for event in soup.select('tr.league-table__match'):  # Selector típico de Betexplorer
        home = event.select_one('.league-table__team--home')
        away = event.select_one('.league-table__team--away')
        score = event.select_one('.league-table__score')
        match = {
            'home': home.text.strip() if home else '',
            'away': away.text.strip() if away else '',
            'score': score.text.strip() if score else ''
        }
        matches.append(match)
    return matches

def main():
    matches = scrape_betexplorer()
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)
    print(f"Estadísticas guardadas en {OUTPUT_PATH}")

if __name__ == "__main__":
    main() 