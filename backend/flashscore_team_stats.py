import requests
from bs4 import BeautifulSoup
import re

BASE_URL = 'https://www.flashscore.es'
SEARCH_URL = BASE_URL + '/busqueda/?q={}'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'https://www.google.com/'
}

def get_team_stats_flashscore(team_name):
    # Buscar el equipo
    search_url = SEARCH_URL.format(team_name.replace(' ', '+'))
    resp = requests.get(search_url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Buscar enlace a la página del equipo
    team_link = None
    for a in soup.select('a'):  # Puede variar el selector
        href = a.get('href', '')
        if '/equipo/' in href:
            team_link = BASE_URL + href
            break
    if not team_link:
        print(f"No se encontró página de equipo para {team_name}")
        return None
    # Scrapeo de la página del equipo
    resp = requests.get(team_link, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Extraer últimos partidos (resultados)
    results = []
    for row in soup.select('div.event__match--static'):  # Puede variar
        score = row.find('div', class_='event__scores')
        if not score:
            continue
        score_text = score.get_text(strip=True)
        m = re.match(r'(\d+)-(\d+)', score_text)
        if m:
            home_goals, away_goals = int(m.group(1)), int(m.group(2))
            results.append((home_goals, away_goals))
    # Calcular medias
    if results:
        goals_for = sum(r[0] for r in results) / len(results)
        goals_against = sum(r[1] for r in results) / len(results)
    else:
        goals_for = goals_against = 0
    stats = {
        'name': team_name,
        'goals_scored_avg': goals_for,
        'goals_conceded_avg': goals_against,
        'last_results': results[:5]
    }
    return stats

if __name__ == "__main__":
    equipo = input("Nombre del equipo: ")
    stats = get_team_stats_flashscore(equipo)
    print(stats) 