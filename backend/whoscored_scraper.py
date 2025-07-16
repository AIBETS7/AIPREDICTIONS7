import requests
from bs4 import BeautifulSoup
import json
import os

WHOSCORED_URL = 'https://www.whoscored.com/Regions/206/Tournaments/4/Spain-LaLiga'
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'data', 'whoscored_laliga.json')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def scrape_whoscored_laliga():
    resp = requests.get(WHOSCORED_URL, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    teams = []
    table = soup.find('table', {'id': 'team-table'})
    if table:
        rows = table.find_all('tr')
        for row in rows[1:]:  # Saltar cabecera
            cols = row.find_all('td')
            if len(cols) > 1:
                team = {
                    'name': cols[1].text.strip(),
                    'matches': cols[2].text.strip() if len(cols) > 2 else '',
                    'goals': cols[3].text.strip() if len(cols) > 3 else '',
                    'shots': cols[4].text.strip() if len(cols) > 4 else '',
                    'possession': cols[5].text.strip() if len(cols) > 5 else ''
                }
                teams.append(team)
    return teams

def main():
    teams = scrape_whoscored_laliga()
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(teams, f, ensure_ascii=False, indent=2)
    print(f"Estadísticas de equipos LaLiga guardadas en {OUTPUT_PATH}")

if __name__ == "__main__":
    main() 