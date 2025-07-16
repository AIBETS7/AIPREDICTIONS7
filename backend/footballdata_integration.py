import requests
import json
import os

# Ruta de salida
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'data', 'footballdata_laliga.json')

# === CONFIGURACIÓN ===
# Sustituye por tu clave de API
FOOTBALLDATA_API_KEY = os.getenv('FOOTBALLDATA_API_KEY', 'TU_API_KEY_AQUI')

# === Football-Data.org ===
def get_laliga_standings_and_results():
    url = 'https://api.football-data.org/v4/competitions/PD/standings'  # PD = LaLiga
    headers = {
        'X-Auth-Token': FOOTBALLDATA_API_KEY
    }
    try:
        standings_resp = requests.get(url, headers=headers)
        standings_resp.raise_for_status()
        standings = standings_resp.json()
    except Exception as e:
        standings = {'error': str(e)}
    # Resultados recientes
    fixtures_url = 'https://api.football-data.org/v4/competitions/PD/matches?status=FINISHED&limit=10'
    try:
        fixtures_resp = requests.get(fixtures_url, headers=headers)
        fixtures_resp.raise_for_status()
        fixtures = fixtures_resp.json()
    except Exception as e:
        fixtures = {'error': str(e)}
    return {'standings': standings, 'recent_results': fixtures}

def main():
    data = get_laliga_standings_and_results()
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Datos de LaLiga guardados en {OUTPUT_PATH}")

if __name__ == "__main__":
    main() 