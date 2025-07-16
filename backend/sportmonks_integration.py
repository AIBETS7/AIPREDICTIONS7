import requests
import json
import os

# Ruta de salida
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'data', 'sportmonks_fixtures.json')

# === CONFIGURACIÓN ===
# Sustituye por tu clave de API
SPORTMONKS_API_KEY = os.getenv('SPORTMONKS_API_KEY', 'TU_API_KEY_AQUI')

# === SPORTMONKS API ===
def get_fixtures():
    url = f'https://api.sportmonks.com/v3/football/fixtures'
    params = {
        'api_token': SPORTMONKS_API_KEY,
        'include': 'localTeam,visitorTeam,league',
        'per_page': 10  # Cambia este valor según lo que necesites
    }
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return {'source': 'sportmonks', 'data': resp.json()}
    except Exception as e:
        return {'source': 'sportmonks', 'error': str(e)}


def main():
    result = get_fixtures()
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Partidos guardados en {OUTPUT_PATH}")

if __name__ == "__main__":
    main() 