import requests
import json
import os

# Ruta de salida
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'data', 'apifootball_fixtures.json')

# === CONFIGURACIÓN ===
# Sustituye por tu clave de API de RapidAPI
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', 'TU_API_KEY_AQUI')
RAPIDAPI_HOST = 'api-football-v1.p.rapidapi.com'

# === API-FOOTBALL ===
def get_fixtures():
    url = f'https://api-football-v1.p.rapidapi.com/v3/fixtures'
    headers = {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': RAPIDAPI_HOST
    }
    params = {
        'league': '140',  # LaLiga (puedes cambiar el ID de liga)
        'season': '2024',
        'next': 10
    }
    try:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        return {'source': 'api-football', 'data': resp.json()}
    except Exception as e:
        return {'source': 'api-football', 'error': str(e)}


def main():
    result = get_fixtures()
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Partidos guardados en {OUTPUT_PATH}")

if __name__ == "__main__":
    main() 